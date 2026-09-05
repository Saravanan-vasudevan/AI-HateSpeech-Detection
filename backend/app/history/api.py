import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from pydantic import BaseModel, Field

from app.history.history import History
from app.history.predictions import Predictions
from app.utils.api import get_current_user
from app.utils.user import User

class PredictionResponseModel(BaseModel):
    '''
    Defines the data structure for a single prediction record when returned via the API.
    This model ensures that the output is consistent, validated, and well-documented.
    '''
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
    text              : str = Field(..., example  = 'This is the text that was analyzed.')
    human_prediction  : bool = Field(..., example = True)
    ai_prediction     : bool = Field(..., example = False)
    human_explanation : str = Field(..., example  = 'I thought this was hateful because...')
    ai_explanation    : str = Field(..., example  = 'The model identified these terms...')
    probability       : float = Field(..., ge = 0, le = 1, example = 0.95)


router = APIRouter()

history_manager: Optional[History] = None

def set_history_manager(manager: History):
    '''
    Dependency injector to set the global history manager instance at application startup.
    '''
    global history_manager

    history_manager = manager

def get_history_manager() -> History:
    '''
    FastAPI dependency to get the current history manager instance.
    Raises a 503 Service Unavailable error if the manager has not been initialized.
    '''
    if history_manager is None:
        raise HTTPException(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail      = 'History manager not initialized.',
        )

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
        predictions_collection = manager.retrieve_predictions(
            username = current_user.get_username(),
            limit    = limit
        )

        return [p.get() for p in predictions_collection]

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
        inserted_id = manager.log_prediction(
            username=current_user.get_username(),
            text              = request.text,
            human             = request.human_prediction,
            ai                = request.ai_prediction,
            human_explanation = request.human_explanation,
            ai_explanation    = request.ai_explanation,
            p                 = request.probability
        )
        return {'status': 'success', 'inserted_id': inserted_id}

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f'Failed to log prediction: {e}',
        )