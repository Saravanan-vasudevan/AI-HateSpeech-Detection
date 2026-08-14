# External library imports
import os
import datetime
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging

# Application imports
from app.utils.database import Database
from app.utils.iam import IAM
from app.utils.api import router as iam_router, get_iam
from app.history.history import History
from app.history.api import router as history_router, set_history_manager
from app.quiz.api import router as quiz_router
from app.quiz.api import set_quiz_dependencies
from app.points.leaderboard import Leaderboard
from app.points.api import router as scores_router, get_leaderboard_service

# Model API impors
from app.models.sklearn_model import SklearnModel
from app.models.hf_generative import HuggingFaceGenerative
from app.models.gemini_generative import GeminiHateSpeechModel
from app.models.ollama_generative import OllamaModel
from app.models.gemini_feedback import FeedbackGenerator
#from models.bilstm_glove_model import BiLSTMGloveModel

from app.models.api import (
    load_model, hf_generative_router,
    sklearn_router, gemini_router,
    ollama_router, feedback_router,bilstm_router
)
# Create a logger
logger = logging.getLogger('astapi_app_logger') 
logger.setLevel(logging.INFO) 

# Create a console handler
handler = logging.StreamHandler()
handler.setLevel(logging.INFO) # Set handler log level

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
if not logger.handlers: # Prevent adding multiple handlers if reloaded
    logger.addHandler(handler)

# Uvicorn often uses the root logger, so this helps catch more.
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])

# Global variables
db_connection               : Optional[Database]              = None
iam_instance                : Optional[IAM]                   = None
history_manager_instance    : Optional[History]               = None
leaderboard_service         : Optional[Leaderboard]           = None


# Application start-up
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_connection, iam_instance, history_manager_instance

    logger.info(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Application starting up...")

    try:
        # credentials.env lives in backend/, one level up from app/. This is
        # a local-dev convenience only -- Cloud Run injects these as real
        # environment variables via --set-secrets, so this call is a no-op there.
        backend_root = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=backend_root / 'credentials.env')

        db_password = os.getenv('DB_PASSWORD')
        db_string_template = os.getenv('DB_STRING')

        if not db_password:
            logger.error('DB_PASSWORD is not set -- refusing to start without it.')
            raise ValueError('DB_PASSWORD environment variable not found.')
        db_password = db_password.strip()

        # Check - Has password been found?
        if db_string_template:
            db_string_template = db_string_template.strip()

        # Else, recording that environment variable not found
        else:
            logger.error('DB_STRING environment variable not found or is empty.')
            raise ValueError('DB_STRING environment variable not found.')
        
        # Performing connection to the database 
        db_connection_string = db_string_template.replace('<db_password>', db_password)
        logger.info(f"Attempting DB connection with string: {db_connection_string.replace(db_password, '****')}")
        db_connection        = Database(connection_string = db_connection_string, db_name = os.getenv('DB_NAME', 'Hate_App'))
  
        # Injecting quiz dependence to access database
        set_quiz_dependencies(db = db_connection)
        print('Quiz dependencies set.')

        # Initialize the Leaderboard service
        leaderboard_service = Leaderboard(db_connection = db_connection)
        print('Leaderboard service initialized.')

        # Connecting the AIM and history object
        iam_instance             = IAM(db=db_connection)
        history_manager_instance = History(db_connection = db_connection, collection_name = os.getenv('PREDICTIONS_COLLECTION', 'predictions'))
        print('IAM and History managers initialized.')

        # Sklearn model is the fast/cheap default; the others load on top of it.
        sklearn_model_path = 'models_state/LR_English_TFIDF_TM_20250629.joblib'
        sklearn_model = SklearnModel(name='Logistic Regression')
        sklearn_model.load(model_path=sklearn_model_path)
        load_model('sklearn', sklearn_model) # Use the generic loader
        print(f"Sklearn model '{sklearn_model.name}' loaded from {sklearn_model_path} and injected.")

        hf_generative_model = HuggingFaceGenerative(use_local_models=True, local_models_dir='./models_state')
        load_model('huggingface', hf_generative_model)
        print(f"HuggingFace model '{hf_generative_model.name}' loaded and injected.")

        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in credentials.env")
        gemini_model = GeminiHateSpeechModel(name='gemini-1.5-flash', api_key=gemini_api_key)
        load_model('gemini', gemini_model)
        print(f"Gemini model '{gemini_model.name}' initialized and injected.")

        ollama_api_url = os.getenv('OLLAMA_API_URL')
        if not ollama_api_url:
            raise ValueError("OLLAMA_API_URL not found in credentials.env")
        ollama_model = OllamaModel(name='ollama-llama3', api_url=ollama_api_url)
        load_model('ollama', ollama_model)
        print(f"Ollama model '{ollama_model.name}' initialized and injected.")

        # BiLSTM + GloVe is trained and evaluated (see app/models/bilstm_glove_model.py)
        # but not wired into the API yet -- re-enable once it's benchmarked
        # against the other four models.
        # bilstm_model = BiLSTMGloveModel(name='BiLSTM_GloVe')
        # bilstm_model.load('models_state/bilstm_glove.pt')
        # load_model('bilstm_glove', bilstm_model)

        feedback_generator = FeedbackGenerator(name='feedback_generator', api_key=gemini_api_key)
        load_model('feedback', feedback_generator)
        print(f"Service '{feedback_generator.name}' initialized and injected.")

        app.dependency_overrides[get_leaderboard_service] = lambda: leaderboard_service
        set_history_manager(history_manager_instance)
        app.dependency_overrides[get_iam] = lambda: iam_instance
        print("Dependencies injected into API routers.")

        hf_generative_model_path = './models_state/generative'
        if not os.path.isdir(hf_generative_model_path):
            print(f"ERROR: Generative model files not found at '{hf_generative_model_path}'")
            print("Run the download script first: python -m app.models.download_hf_generative")
            raise FileNotFoundError('Essential model files are missing. Application cannot start.')

    except Exception as e:
        print(f"CRITICAL: Application startup failed: {e}")
        raise RuntimeError(f"Failed to initialize essential services: {e}") from e

    yield

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Application shutting down...")
    if db_connection:
        db_connection.close_connection()
        print("Database connection closed.")

# FastAPI application
app = FastAPI(
    title       = 'Hate Speech Detection API',
    description = 'Provides access to multiple hate speech detection models.',
    version     = '1.0.0',
    lifespan    = lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ['http://localhost:5173', 'null', 'http://127.0.0.1:5500', 'http://localhost:5500' ],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# API router
app.include_router(iam_router, tags = ['IAM Authentication'])
app.include_router(history_router, tags = ['Predictions History'])

# Add the Sklearn model router
app.include_router(
    sklearn_router,
    prefix = '/sklearn',
    tags   = ['Sklearn Model']
)

# Add the HuggingFace model router
app.include_router(
    hf_generative_router,
    prefix = '/hf_generative', 
    tags   = ['HuggingFace Generative Model']
)
# Add the Gemini model router 
app.include_router(
    gemini_router,
    prefix = '/gemini',
    tags   = ['Gemini Model']
)
# Adding the Ollama model router
app.include_router(
    ollama_router,
    prefix = '/ollama',
    tags   = ['Ollama Model']
)
# Adding Gemini based feedback module
app.include_router(
    feedback_router,
    prefix = '/feedback',
    tags   = ['Feedback Service']
)

# Adding the quiz router
app.include_router(
    quiz_router,
    prefix = '/quiz',
    tags   = ['Quiz']
)
# Adding the history router
app.include_router(
    history_router,
    prefix = '/history',
    tags   = ['Predictions History'],

)
# Adding the scores and leaderboard router
app.include_router(
    scores_router,
    prefix = '/scores',
    tags   = ['Scores & Leaderboard']
)

# Add BiLSTM GloVe router
#app.include_router(
#    bilstm_router,
#    prefix = '/bilstm',
#    tags   = ['BiLSTM-GloVe Model']
#)

