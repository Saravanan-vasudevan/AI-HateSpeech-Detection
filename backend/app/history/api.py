# Import standard libraries
import datetime

# Import third-party libraries
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from pydantic import BaseModel, Field

# Import local application modules
from app.history.history import History
from app.history.predictions import Predictions
from app.utils.api import get_current_user
from app.utils.user import User

class PredictionResponseModel(BaseModel):
    '''
    Defines the data structure for a single prediction record when returned via the API.
    This model ensures that the output is consistent, validated, and well-documented.
    '''
    # :Properties of the response
    username          : str = Field(..., example  = 'john_doe')
    datetime          : str = Field(..., example  = '2025-07-17T10:55:46.123Z')
    text              : str = Field(..., example  = 'This is the text that was analyzed.')
    human_prediction  : bool = Field(..., example = True)
    ai_prediction     : bool = Field(..., example = False)
    score             : int = Field(..., example  = 0)
    human_explanation : str = Field(..., example  = 'I thought this was hateful because...')
    ai_explanation    : str = Field(..., example  = 'The model identified these terms...')
    probability       : float = Field(..., ge = 0, le = 1, example = 0.95)

class PredictionLogRequest(BaseModel):
    '''
    Defines the data structure for the request body when logging a new prediction.
    '''
    # Properties required to log a 
    text              : str = Field(..., example  = 'This is the text that was analyzed.')
    human_prediction  : bool = Field(..., example = True)
    ai_prediction     : bool = Field(..., example = False)
    human_explanation : str = Field(..., example  = 'I thought this was hateful because...')
    ai_explanation    : str = Field(..., example  = 'The model identified these terms...')
    probability       : float = Field(..., ge = 0, le = 1, example = 0.95)


# Create the API router for this module
router = APIRouter()

# Global variable - Store history manager
history_manager: Optional[History] = None

def set_history_manager(manager: History):
    '''
    Dependency injector to set the global history manager instance at application startup.
    '''
    # Specifying history manager as global
    global history_manager

    # Assigning the history manager
    history_manager = manager

def get_history_manager() -> History:
    '''
    FastAPI dependency to get the current history manager instance.
    Raises a 503 Service Unavailable error if the manager has not been initialized.
    '''
    # Check - Has history manager been set?
    if history_manager is None:
        raise HTTPException(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail      = 'History manager not initialized.',
        )
    
    # Else, returning the history manager
    return history_manager


@router.get('/', response_model = List[PredictionResponseModel])
async def get_predictions(
    manager: History = Depends(get_history_manager),
    current_user: User = Depends(get_current_user),
    limit: int = Query(100, ge=0, le=1000, description='Max number of records to return.')):
    '''
    Retrieves historical prediction records for the currently authenticated user,
    sorted from newest to oldest.
    '''
    try:
        # Fetch predictions only for the logged-in user
        predictions_collection = manager.retrieve_predictions(
            username = current_user.get_username(),
            limit    = limit
        )

        # Convert the internal Prediction objects to dictionaries for the response
        return [p.get() for p in predictions_collection]
    
    # Else, something goes wrong that I need to address
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f'An unexpected error occurred: {e}',
        )

@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_prediction(
    request: PredictionLogRequest,
    manager: History = Depends(get_history_manager),
    current_user: User = Depends(get_current_user)):
    '''
    Logs a new prediction event to the authenticated user's history.
    '''
    try:
        # Call the log_prediction method with data from the request and the user's token
        inserted_id = manager.log_prediction(
            username=current_user.get_username(),
            text              = request.text,
            human             = request.human_prediction,
            ai                = request.ai_prediction,
            human_explanation = request.human_explanation,
            ai_explanation    = request.ai_explanation,
            p                 = request.probability
        )
        # Return a success message with the ID of the new database record
        return {'status': 'success', 'inserted_id': inserted_id}
    
    # Else, something goes wrong....
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f'Failed to log prediction: {e}',
        )