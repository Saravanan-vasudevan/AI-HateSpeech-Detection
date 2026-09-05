from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.quiz.game import Game
from app.utils.database import Database

router = APIRouter()

_current_game     : Optional[Game]     = None
_current_username : Optional[str]      = None
_db_instance      : Optional[Database] = None

def set_quiz_dependencies(db: Database):
    global _db_instance
    _db_instance = db

def get_current_game() -> Game:
    if _current_game is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = 'No active game. Please start a game first.'
        )

    return _current_game


class GameConfig(BaseModel):
    '''
    Properties of the game itself
    '''
    username      : str
    hardness      : int
    num_questions : int

class QuestionResponse(BaseModel):
    '''
    Representations of the questions
    that will populate the GUI
    '''
    question_text  : str
    options        : list[str]

class AnswerSubmission(BaseModel):
    '''
    The question has been selected
    as the users answer
    '''
    selected_answer_index: int

class ScoreResponse(BaseModel):
    '''
    Stores the score the user
    has acheived in the quiz this
    time
    '''
    username : str
    score    : int
    message  : str


@router.post('/start', response_model = QuestionResponse, summary = 'Start a new quiz game')
async def start_game(config: GameConfig) -> None:
    global _current_game, _current_username, _db_instance

    if _db_instance is None:
        raise RuntimeError('Database dependency not set for quiz API.')

    try:

        _current_username = config.username

        _current_game = Game(
            db         = _db_instance,
            collection = 'questions',
            hardness   = config.hardness,
            questions  = config.num_questions,
            username   = config.username
        )
        question_text, options = _current_game.get_question()

        return QuestionResponse(question_text = question_text, options = options)

    except (TypeError, ValueError, RuntimeError) as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"Failed to start game: {e}"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An unexpected error occurred: {e}"
        )

@router.get('/next_question', response_model = QuestionResponse, summary = 'Get the next question')
async def get_next_question() -> QuestionResponse:
    game = get_current_game()

    if not game.has_question():
        raise HTTPException(
            status_code = status.HTTP_204_NO_CONTENT,
            detail      = 'No more questions available in the quiz.'
        )

    try:
        question_text, options = game.get_question()
        return QuestionResponse(question_text=question_text, options=options)

    except IndexError:
        raise HTTPException(
            status_code = status.HTTP_204_NO_CONTENT,
            detail      = 'No more questions available in the quiz.'
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An unexpected error occurred while getting question: {e}"
        )


@router.post("/submit_answer", summary="Submit an answer to the current question")
async def submit_answer(answer_data: AnswerSubmission) -> dict:
    game = get_current_game()

    try:
        is_correct = game.check_answer(answer_data.selected_answer_index)
        return {"is_correct": is_correct}

    except (TypeError, RuntimeError, IndexError) as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"Error submitting answer: {e}"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An unexpected error occurred while submitting answer: {e}"
        )


@router.get("/score", response_model=ScoreResponse, summary="Get the current score")
async def get_score():
    game = get_current_game()
    global _current_username

    score = game.get_score()

    message = 'Quiz is ongoing.'

    if not game.has_question():

        try:
            game.store_score()
            message ='Quiz finished! Score stored successfully.'

        except Exception as e:
            message = f"Quiz finished, but failed to store score: {e}"
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail      = message
            )

    return ScoreResponse(username = _current_username, score = score * 10, message = message)

@router.get('/has_question', summary = 'Check if there are more questions')
async def check_has_question() -> dict:
    game = get_current_game()

    return {"has_more_questions": game.has_question()}
