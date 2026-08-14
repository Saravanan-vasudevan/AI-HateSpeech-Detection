
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict
from app.models.hf_generative import HuggingFaceGenerative
from app.models.sklearn_model import SklearnModel
from app.models.gemini_generative import GeminiHateSpeechModel
from app.models.ollama_generative import OllamaModel
from app.models.gemini_feedback import FeedbackGenerator
from app.models.bilstm_glove_model import BiLSTMGloveModel


############################################################
#                   Shared Requests                        #
############################################################ 
# One set of request/response models can be used for all endpoints.
class PredictionRequest(BaseModel):
    '''
    A generic request model for any text-based prediction.
    This has been refactored and design to work across all
    the models we want to develop
    '''
    # Specifying the request needs a text argument
    text: str = Field(..., min_length = 1, example = 'This is some text to analyze.')

class PredictionResponse(BaseModel):
    '''
    A generic response model for any model's prediction.
    Again, this is an improvement of the refactoring to
    minimise code repitition
    '''
    # Properties that are predicted during the hate speech
    is_hate_speech         : bool
    hate_speech_probability: float = Field(..., ge=0, le=1)
    explanation            : str
    input_text             : str

class FeedbackRequest(BaseModel):
    '''
    Defines the data needed to generate feedback.
    '''
    # Properties of the feedback that is sent to the model
    student_prediction  : bool = Field(..., example = True)
    student_explanation : str  = Field(..., example = 'The text uses dehumanizing language.')
    ai_prediction       : bool = Field(..., example = True)
    ai_explanation      : str  = Field(..., example = 'The model identified dehumanizing slurs.')

class FeedbackResponse(BaseModel):
    '''
    Defines the structure of the returned feedback.
    '''
    # The feedback is a single field
    feedback_text: str = Field(..., example = 'That\'s great thinking! You correctly noted the dehumanizing language...')

############################################################
#                Shared Model Load                         #
############################################################

# List of all the models to use
_loaded_models: Dict[str, BaseModel] = {}

def load_model(name: str, model: BaseModel):
    '''
    Loads a model instance into the central registry.
    
    Input args:
    - name (str) : Internal name of the model
    - model (BaseModel) :
    '''
    # Accesin the global variable for models
    global _loaded_models

    # Specifying that we are storing the model
    # against its name
    _loaded_models[name] = model

def get_model_dependency(model_name: str) -> callable:
    '''
    A dependency factory.
    This function returns another function, which is the actual dependency
    FastAPI will use to retrieve a loaded model by its name.
    '''
    def _get_model() -> BaseModel:
        '''
        Hidden method that actually accesses the model
        and raises an exception in the model cannot be
        located
        '''
        # Check - Is the internal model name already stored?
        if model_name not in _loaded_models:

            # ... If not, raising an exception
            raise HTTPException(
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
                detail      = f"Model '{model_name}' is not loaded."
            )
        
        # Else, returning the model to the parent method
        return _loaded_models[model_name]
    
    # Returning the output to the method
    return _get_model


############################################################
#         Model 1 - HuggingFaceGenerative                  #
#             (hf_generati
# ve.py)                           #
############################################################

# Router for the HF API
hf_generative_router = APIRouter()

@hf_generative_router.post('/predict', response_model = PredictionResponse,
    summary='Predict hate speech with HuggingFace model')
async def predict_hf_generative(
    request: PredictionRequest,
    model: HuggingFaceGenerative = Depends(get_model_dependency('huggingface'))
) -> PredictionResponse:
    '''
    Returns a HuggingFace prediction for the model

    Input args:
    - request (PredictionRequest)  : PyDantic object with text attribute
    - model (HuggingFaceGenerative): Pre-trained HF model for use
    
    Return:
    - (PredictionResponse) : Result with all outputs
    ''' 
    # Putting inside a try / catch to handle errors
    try:
         
        # ... Extracting the text from the request
        input_text = request.text

        # ... Making predicted probability and test
        hate_score            = model.predict(input_text)
        full_explanation_text = model.predict_text(input_text)

        # ... Putting a placeholder (in case explanation is not available)
        explanation_part = 'Explanation not available.'

        # Check - Has the explanation been provided?
        if 'Contextual Explanation:' in full_explanation_text:

            # ... If so, overriding the explanation
            explanation_part = full_explanation_text.split('Contextual Explanation:', 1)[1].strip()

        # Creating our prediction response
        return PredictionResponse(
            is_hate_speech          = (hate_score > 0.5),
            hate_speech_probability = hate_score,
            explanation             = explanation_part,
            input_text              = input_text
        )
    
    # Exception ... Something went wrong the prediction
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An error occurred during prediction: {str(e)}"
        )
    

############################################################
#         Model 2 - SklearnModel                           #
#             (sklearn_model.py)                           #
############################################################

# Creating our router object
sklearn_router = APIRouter()

@sklearn_router.post('/predict', response_model = PredictionResponse,
                    summary='Predict hate speech with Sklearn model')
async def predict_sklearn(
    request: PredictionRequest,
    model: SklearnModel = Depends(get_model_dependency('sklearn'))
) -> PredictionResponse:
    '''
    Makes a prediction with the sci-kit learn model

    Input args:
    - request (PredictionRequest) : PyDantic model with text attribute
    - model (SklearnModel)        : Sci-kit learn model pre-trained for classification
    
    Return:
    - PredictionResponse : Result
    '''
    # Making a prediction 
    # - Exceptions
    try:

        # Retrieving the probabilities and text
        probability      = model.predict(request.text)
        explanation_text = model.predict_text(text=request.text)

        # Converting to standardise response
        return PredictionResponse(
            is_hate_speech          = (probability > 0.5),
            hate_speech_probability = probability,
            explanation             = explanation_text,
            input_text              = request.text
        )
    
    # Throwing an error
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Prediction error: {e}")
    
############################################################
#           Model 3 - GeminiHateSpeechModel                #
#             (gemini_generative.py)                       #
############################################################

# Creating a router for the Gemini Model
gemini_router = APIRouter()

@gemini_router.post('/predict', response_model = PredictionResponse,
    summary='Predict hate speech with Gemini model')
async def predict_gemini(
    request: PredictionRequest,
    model: GeminiHateSpeechModel = Depends(get_model_dependency('gemini'))
) -> PredictionResponse:
    '''
    Makes a prediction with the Gemini Model

    Input args:
    - request (PredictionRequest)   : Standardised request with text attribute
    - model (GeminiHateSpeechModel) : Gemini LLM
    '''
    # Handling the prediction
    try:

        # ... Extracting the text from the input
        input_text = request.text

        # ... Performing pre-processing to the prompt
        prompt = model.preprocess(input_text)

        # ... Making a prediction of probability and model
        probability = model.predict(prompt)
        explanation = model.predict_text(prompt)

        # ... Returning a structured response
        return PredictionResponse(
            is_hate_speech          = (probability > 0.5),
            hate_speech_probability = probability,
            explanation             = explanation,
            input_text              = input_text
        )
    
    # ... Except an error has been raised
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An error occurred during Gemini prediction: {str(e)}"
        )
    
############################################################
#           Model 4 - OllamaModel (Self-Hosted)            #
#              (ollama_generative.py)                      #
############################################################

# Create a router for the Ollama Model
ollama_router = APIRouter()

@ollama_router.post('/predict', response_model=PredictionResponse,
    summary='Predict hate speech with self-hosted Ollama model')
async def predict_ollama(
    request: PredictionRequest,
    model: OllamaModel = Depends(get_model_dependency('ollama'))) -> PredictionResponse:
    '''
    Makes a prediction with the self-hosted Ollama Model.

    Input args:
    - request (PredictionRequest): Standardised request with text attribute.
    - model (OllamaModel)      : Self-hosted Ollama LLM.
    '''
    # Handle the prediction inside a try/except block.
    try:
        # Extract the text from the request.
        input_text = request.text

        # Preprocess the text into the JSON payload for the Ollama API.
        payload = model.preprocess(input_text)

        # Needs to be performed in async fashion
        probability = await model.predict(payload)
        explanation = await model.predict_text(payload)

        # Return the structured response.
        return PredictionResponse(
            is_hate_speech          = (probability > 0.5),
            hate_speech_probability = probability,
            explanation             = explanation,
            input_text              = input_text
        )

    # Handle any exceptions during the prediction.
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An error occurred during Ollama prediction: {str(e)}"
        )
############################################################
#         Model 5 - BiLSTMGloveModel                       #
#             (bilstm_glove_model.py)                      #
############################################################

bilstm_router = APIRouter()

@bilstm_router.post('/predict', response_model=PredictionResponse,
    summary='Predict hate speech with BiLSTM + GloVe model')
async def predict_bilstm(
    request: PredictionRequest,
    model: BiLSTMGloveModel = Depends(get_model_dependency('bilstm_glove'))
) -> PredictionResponse:
    '''
    Makes a prediction using the BiLSTM + GloVe model.

    Input:
    - request: PredictionRequest containing input text
    - model: Loaded BiLSTMGloveModel via dependency injection

    Output:
    - PredictionResponse with prediction, probability, explanation, and input
    '''
    try:
        input_text = request.text
        probability = model.predict(input_text)
        explanation = model.predict_text(input_text)

        return PredictionResponse(
            is_hate_speech=(probability > 0.5),
            hate_speech_probability=probability,
            explanation=explanation,
            input_text=input_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An error occurred during BiLSTM prediction: {str(e)}'
        )

############################################################
#         Service 1 - FeedbackGenerator                    #
############################################################

# Creating the router for the feedback
feedback_router = APIRouter()

@feedback_router.post('/generate', response_model = FeedbackResponse,
    summary='Generate pedagogical feedback for a student')
async def generate_feedback(
    request: FeedbackRequest, 
    model: FeedbackGenerator = Depends(get_model_dependency('feedback'))) -> FeedbackResponse:
    '''
    Takes student and AI predictions/explanations and generates tailored feedback.

    Input args:
    - request (FeedbackGenerator) : PyDantic representation for the model
    - model (FeedbackGenerator)   : Gemini model for training

    Return:
    - (FeedbackResponse) : PyDantic representation to go back to model
    '''
    # Handle the feedback generation in a try/except block
    try:

        # Call the generate method on the injected model instance
        feedback_text = model.generate(
            student_prediction  = request.student_prediction,
            student_explanation = request.student_explanation,
            ai_prediction       = request.ai_prediction,
            ai_explanation      = request.ai_explanation
        )
        # Return the generated feedback in the response model
        return FeedbackResponse(feedback_text = feedback_text)
    
    # Handle any exceptions during feedback generation
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f'An error occurred during feedback generation: {str(e)}'
        )