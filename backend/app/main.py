import os
import datetime
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.utils.database import Database
from app.utils.iam import IAM
from app.utils.api import router as iam_router, get_iam
from app.history.history import History
from app.history.api import router as history_router, set_history_manager
from app.quiz.api import router as quiz_router
from app.quiz.api import set_quiz_dependencies
from app.points.leaderboard import Leaderboard
from app.points.api import router as scores_router, get_leaderboard_service

from app.models.sklearn_model import SklearnModel
from app.models.hf_generative import HuggingFaceGenerative
from app.models.gemini_generative import GeminiHateSpeechModel
from app.models.ollama_generative import OllamaModel
from app.models.gemini_feedback import FeedbackGenerator
from app.models.api import (
    load_model, hf_generative_router,
    sklearn_router, gemini_router,
    ollama_router, feedback_router,
)

logger = logging.getLogger('fastapi_app_logger')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])

# These get populated during startup and torn down on shutdown.
db_connection               : Optional[Database]    = None
iam_instance                : Optional[IAM]         = None
history_manager_instance    : Optional[History]     = None
leaderboard_service         : Optional[Leaderboard] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Wire up the DB, models, and services before the first request.

    credentials.env is a local-dev convenience -- Cloud Run injects
    env vars via --set-secrets so the dotenv call is a no-op there.
    """
    global db_connection, iam_instance, history_manager_instance

    logger.info(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] Starting up...")

    try:
        backend_root = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=backend_root / 'credentials.env')

        db_password = os.getenv('DB_PASSWORD')
        db_string_template = os.getenv('DB_STRING')

        if not db_password:
            raise ValueError('DB_PASSWORD not set -- cannot connect to Mongo.')
        db_password = db_password.strip()

        if not db_string_template:
            raise ValueError('DB_STRING not set -- need a connection string template.')
        db_string_template = db_string_template.strip()

        db_connection_string = db_string_template.replace('<db_password>', db_password)
        logger.info(f"Connecting to DB: {db_connection_string.replace(db_password, '****')}")
        db_connection = Database(
            connection_string=db_connection_string,
            db_name=os.getenv('DB_NAME', 'Hate_App'),
        )

        set_quiz_dependencies(db=db_connection)
        leaderboard_service = Leaderboard(db_connection=db_connection)
        iam_instance = IAM(db=db_connection)
        history_manager_instance = History(
            db_connection=db_connection,
            collection_name=os.getenv('PREDICTIONS_COLLECTION', 'predictions'),
        )

        # Load models -- sklearn is the fast/cheap baseline, then the heavier ones.
        sklearn_model_path = 'models_state/LR_English_TFIDF_TM_20250629.joblib'
        if os.path.isfile(sklearn_model_path):
            sklearn_model = SklearnModel(name='Logistic Regression')
            sklearn_model.load(model_path=sklearn_model_path)
            load_model('sklearn', sklearn_model)
            logger.info("Loaded the local sklearn model")
        else:
            logger.warning("Sklearn artifact not found; /sklearn/predict will return 503")

        hf_model = HuggingFaceGenerative(use_local_models=True, local_models_dir='./models_state')
        load_model('huggingface', hf_model)
        print(f"Loaded HuggingFace model: {hf_model.name}")

        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            gemini_model = GeminiHateSpeechModel(name='gemini-1.5-flash', api_key=gemini_api_key)
            load_model('gemini', gemini_model)
            feedback_gen = FeedbackGenerator(name='feedback_generator', api_key=gemini_api_key)
            load_model('feedback', feedback_gen)
        else:
            logger.warning("GEMINI_API_KEY is not set; Gemini endpoints will return 503")

        ollama_api_url = os.getenv('OLLAMA_API_URL')
        if ollama_api_url:
            ollama_model = OllamaModel(name='ollama-llama3', api_url=ollama_api_url)
            load_model('ollama', ollama_model)
        else:
            logger.warning("OLLAMA_API_URL is not set; Ollama endpoint will return 503")

        # Dependency overrides so routers get the live instances.
        app.dependency_overrides[get_leaderboard_service] = lambda: leaderboard_service
        set_history_manager(history_manager_instance)
        app.dependency_overrides[get_iam] = lambda: iam_instance

        # Sanity-check: the generative model dir must exist (downloaded separately).
        gen_path = './models_state/generative'
        if not os.path.isdir(gen_path):
            print(f"ERROR: {gen_path} not found. Run: python -m app.models.download_hf_generative")
            raise FileNotFoundError('Generative model files missing.')

        print("All models and services ready.")

    except Exception as e:
        print(f"CRITICAL startup failure: {e}")
        raise RuntimeError(f"Startup failed: {e}") from e

    yield

    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] Shutting down...")
    if db_connection:
        db_connection.close_connection()


app = FastAPI(
    title='Hate Speech Detection API',
    description='Multi-model hate speech detection and feedback service.',
    version='1.0.0',
    lifespan=lifespan,
)

# CORS -- only allow real origins. "null" was here before but that's an
# open door for file:// and sandboxed iframe requests; remove it.
# In production, swap the placeholder below for your actual domain.
ALLOWED_ORIGINS = [
    'http://localhost:5173',       # Vite dev server
    'http://127.0.0.1:5173',
    'http://localhost:5500',       # VS Code Live Server
    'http://127.0.0.1:5500',
    # 'https://your-production-domain.example.com',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods     = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers     = ['*'],
)

# --- Routers ---
app.include_router(iam_router, tags=['IAM Authentication'])
app.include_router(sklearn_router,        prefix='/sklearn',       tags=['Sklearn Model'])
app.include_router(hf_generative_router,  prefix='/hf_generative', tags=['HuggingFace Generative Model'])
app.include_router(gemini_router,         prefix='/gemini',        tags=['Gemini Model'])
app.include_router(ollama_router,         prefix='/ollama',        tags=['Ollama Model'])
app.include_router(feedback_router,       prefix='/feedback',      tags=['Feedback Service'])
app.include_router(quiz_router,           prefix='/quiz',          tags=['Quiz'])
app.include_router(history_router,        prefix='/history',       tags=['Predictions History'])
app.include_router(scores_router,         prefix='/scores',        tags=['Scores & Leaderboard'])
