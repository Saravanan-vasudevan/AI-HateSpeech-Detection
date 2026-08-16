from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict
from app.models.hf_generative import HuggingFaceGenerative
from app.models.sklearn_model import SklearnModel
from app.models.gemini_generative import GeminiHateSpeechModel
from app.models.ollama_generative import OllamaModel
from app.models.gemini_feedback import FeedbackGenerator


# ---- Request / Response schemas (shared across all model endpoints) ----

class PredictionRequest(BaseModel):
    """Input payload for any /predict endpoint."""
    text: str = Field(..., min_length=1, example='This is some text to analyze.')

class PredictionResponse(BaseModel):
    is_hate_speech         : bool
    hate_speech_probability: float = Field(..., ge=0, le=1)
    explanation            : str
    input_text             : str

class FeedbackRequest(BaseModel):
    student_prediction  : bool = Field(..., example=True)
    student_explanation : str  = Field(..., example='The text uses dehumanizing language.')
    ai_prediction       : bool = Field(..., example=True)
    ai_explanation      : str  = Field(..., example='The model identified dehumanizing slurs.')

class FeedbackResponse(BaseModel):
    feedback_text: str


# ---- Model registry ----

_loaded_models: Dict[str, BaseModel] = {}

def load_model(name: str, model: BaseModel):
    """Register a model instance so endpoints can look it up by name."""
    global _loaded_models
    _loaded_models[name] = model

def get_model_dependency(model_name: str) -> callable:
    """FastAPI dependency factory -- returns a callable that fetches `model_name`
    from the registry, or 503s if it hasn't been loaded yet."""
    def _get():
        if model_name not in _loaded_models:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=f"Model '{model_name}' is not loaded.")
        return _loaded_models[model_name]
    return _get


# ---- HuggingFace (RoBERTa classifier + GPT-Neo explanation) ----

hf_generative_router = APIRouter()

@hf_generative_router.post('/predict', response_model=PredictionResponse,
    summary='Predict hate speech with HuggingFace model')
async def predict_hf_generative(
    request: PredictionRequest,
    model: HuggingFaceGenerative = Depends(get_model_dependency('huggingface'))
) -> PredictionResponse:
    """Run the HF classifier and extract the contextual explanation if the
    generative model produced one."""
    try:
        input_text = request.text
        hate_score = model.predict(input_text)
        full_text  = model.predict_text(input_text)

        # The generative model prepends "Prediction: ... Contextual Explanation: ..."
        explanation = 'Explanation not available.'
        if 'Contextual Explanation:' in full_text:
            explanation = full_text.split('Contextual Explanation:', 1)[1].strip()

        return PredictionResponse(
            is_hate_speech=hate_score > 0.5,
            hate_speech_probability=hate_score,
            explanation=explanation,
            input_text=input_text,
        )
    except Exception as e:
        raise HTTPException(500, detail=f"HuggingFace prediction failed: {e}")


# ---- Sklearn (TF-IDF + Logistic Regression) ----

sklearn_router = APIRouter()

@sklearn_router.post('/predict', response_model=PredictionResponse,
    summary='Predict hate speech with Sklearn model')
async def predict_sklearn(
    request: PredictionRequest,
    model: SklearnModel = Depends(get_model_dependency('sklearn'))
) -> PredictionResponse:
    """Lightweight TF-IDF + LR prediction -- usually sub-5ms."""
    try:
        prob = model.predict(request.text)
        return PredictionResponse(
            is_hate_speech=prob > 0.5,
            hate_speech_probability=prob,
            explanation=model.predict_text(text=request.text),
            input_text=request.text,
        )
    except Exception as e:
        raise HTTPException(500, detail=f"Sklearn prediction error: {e}")


# ---- Gemini (cloud LLM) ----

gemini_router = APIRouter()

@gemini_router.post('/predict', response_model=PredictionResponse,
    summary='Predict hate speech with Gemini model')
async def predict_gemini(
    request: PredictionRequest,
    model: GeminiHateSpeechModel = Depends(get_model_dependency('gemini'))
) -> PredictionResponse:
    """Send the text to Gemini and parse the structured JSON it returns."""
    input_text = request.text
    prompt = model.preprocess(input_text)
    try:
        probability = model.predict(prompt)
        explanation = model.predict_text(prompt)
    except Exception as e:
        raise HTTPException(500, detail=f"Gemini prediction failed: {e}")

    return PredictionResponse(
        is_hate_speech=probability > 0.5,
        hate_speech_probability=probability,
        explanation=explanation,
        input_text=input_text,
    )


# ---- Ollama (self-hosted Llama 3) ----

ollama_router = APIRouter()

@ollama_router.post('/predict', response_model=PredictionResponse,
    summary='Predict hate speech with self-hosted Ollama model')
async def predict_ollama(
    request: PredictionRequest,
    model: OllamaModel = Depends(get_model_dependency('ollama'))
) -> PredictionResponse:
    """Calls the self-hosted Ollama endpoint. Both predict methods are async
    because the underlying httpx client is async."""
    input_text = request.text
    payload = model.preprocess(input_text)
    try:
        probability = await model.predict(payload)
        explanation = await model.predict_text(payload)
    except Exception as e:
        raise HTTPException(500, detail=f"Ollama prediction failed: {e}")

    return PredictionResponse(
        is_hate_speech=probability > 0.5,
        hate_speech_probability=probability,
        explanation=explanation,
        input_text=input_text,
    )


# ---- Feedback generator (Gemini-backed pedagogical feedback) ----

feedback_router = APIRouter()

@feedback_router.post('/generate', response_model=FeedbackResponse,
    summary='Generate pedagogical feedback for a student')
async def generate_feedback(
    request: FeedbackRequest,
    model: FeedbackGenerator = Depends(get_model_dependency('feedback'))
) -> FeedbackResponse:
    """Compare the student's prediction/explanation against the AI's and
    return Socratic-style feedback."""
    try:
        text = model.generate(
            student_prediction=request.student_prediction,
            student_explanation=request.student_explanation,
            ai_prediction=request.ai_prediction,
            ai_explanation=request.ai_explanation,
        )
        return FeedbackResponse(feedback_text=text)
    except Exception as e:
        raise HTTPException(500, detail=f"Feedback generation failed: {e}")
