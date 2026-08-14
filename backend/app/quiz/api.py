# your_quiz_project/quiz/api.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

# Import your Quiz Game specific classes
from app.quiz.game import Game
from app.utils.database import Database 

# Quiz end points
router = APIRouter() 

# Global Game instance - Handled here
_current_game     : Optional[Game]     = None
_current_username : Optional[str]      = None
_db_instance      : Optional[Database] = None 

def set_quiz_dependencies(db: Database):
    '''
    Function to set database dependency for the quiz router

    Input args:
    - db : Database - Connected MongoDB cluster

    Return:
    - None
    '''
    # Defining our DB instance as global
    global _db_instance
    _db_instance = db

def get_current_game() -> Game:
    '''
    Retrieves the game, that has been set global

    Input args:
    - None

    Return:
    - (Game) : Game set (assuming that is correct)
    '''
    # Check 1 - Has the game been set?
    if _current_game is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = 'No active game. Please start a game first.'
        )
    
    # Else, return the game
    return _current_game


class GameConfig(BaseModel):
    '''
    Properties of the game itself
    '''
    username      : str  # Username of the user playing the game
    hardness      : int  # How hard the game is (0, 1, 2)
    num_questions : int  # Specified number of questions (you want)

class QuestionResponse(BaseModel):
    '''
    Representations of the questions
    that will populate the GUI
    '''
    question_text  : str         # The question itself
    options        : list[str]   # List of 4 multiple choice options

class AnswerSubmission(BaseModel):
    '''
    The question has been selected
    as the users answer
    '''
    selected_answer_index: int  # Index user has selected

class ScoreResponse(BaseModel):
    '''
    Stores the score the user
    has acheived in the quiz this
    time
    '''
    username : str    # Username of user playing the game
    score    : int    # Score they achieved
    message  : str    # Message to add  


# API post to start a new game
@router.post('/start', response_model = QuestionResponse, summary = 'Start a new quiz game')
async def start_game(config: GameConfig) -> None:
    '''
    Starts a new quiz game with the specified configuration.
    Returns the first question.
    
    Input args:
    - config (GameConfig) : Properties of the quiz game itself

    Return:
    - None
    '''
    # Global variables
    # - This need to be out of scope of just the method for the
    #   quick to work properly
    global _current_game, _current_username, _db_instance

    # Check 1 - Has a database actually be setup?
    if _db_instance is None:
        raise RuntimeError('Database dependency not set for quiz API.')

    # Checking the gam can be correctly set up
    try:

        # ... Setting the global variabe
        _current_username = config.username

        # ... Setting up the game itself and
        #     storing as a game
        _current_game = Game(
            db         = _db_instance,
            collection = 'questions',
            hardness   = config.hardness,
            questions  = config.num_questions,
            username   = config.username
        )
        # Question - Retrieving the first question of the game
        question_text, options = _current_game.get_question()

        # Returning the question for user in game
        return QuestionResponse(question_text = question_text, options = options)
    
    # Exception
    # - There may be a few reasons why the game cannot be run
    except (TypeError, ValueError, RuntimeError) as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"Failed to start game: {e}"
        )
    
    # An unhandled error time - in case unanticipated errors
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An unexpected error occurred: {e}"
        )

# Method to retrieve the next question
@router.get('/next_question', response_model = QuestionResponse, summary = 'Get the next question')
async def get_next_question() -> QuestionResponse:
    '''
    Retrieves the next question in the current quiz game.
    
    Input args:
    - None

    Return:
    - QuestionResponse : Information about the question and its options
    '''
    # Use helper method to retrieve the question
    game = get_current_game()
    
    # Whilst we have the ability to check if there is a next question,
    # there is a possibility of overspill and so this check is needed
    if not game.has_question():
        raise HTTPException(
            status_code = status.HTTP_204_NO_CONTENT,
            detail      = 'No more questions available in the quiz.'
        )

    # Getting an retrieving a question
    try:
        question_text, options = game.get_question()
        return QuestionResponse(question_text=question_text, options=options)
    
    # Catching an index error (in case get_question raises a problem)
    except IndexError: 
        raise HTTPException(
            status_code = status.HTTP_204_NO_CONTENT,
            detail      = 'No more questions available in the quiz.'
        )
    
    # Anything else (like an internal service error)
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An unexpected error occurred while getting question: {e}"
        )


@router.post("/submit_answer", summary="Submit an answer to the current question")
async def submit_answer(answer_data: AnswerSubmission) -> dict:
    '''
    Submits an answer for the current question.
    Returns whether the answer was correct.
    
    Return:
    - (dict) : This is encapsulated in a dict without boolean
    '''
    # Using the helper method to get game
    game = get_current_game() 

    # Performing the check
    try:
        is_correct = game.check_answer(answer_data.selected_answer_index)
        return {"is_correct": is_correct}
    
    # Expected possible exceptions
    except (TypeError, RuntimeError, IndexError) as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"Error submitting answer: {e}"
        )
    
    # Unexpected exception
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An unexpected error occurred while submitting answer: {e}"
        )


@router.get("/score", response_model=ScoreResponse, summary="Get the current score")
async def get_score():
    '''
    Retrieves the current score of the active game.
    Also stores the final score if the quiz is completed.

    Input args:
    - None

    Return: 
    - message
    '''
    # Brining in scope the current game
    game = get_current_game() 
    global _current_username 

    # Obtaining the  score
    score = game.get_score()

    # Assuming the game is on-going
    message = 'Quiz is ongoing.'

    # Checking if we still have qustions
    if not game.has_question():

        # Storing the score
        try:
            game.store_score()
            message ='Quiz finished! Score stored successfully.'

        # ... An interval service error
        except Exception as e:
            message = f"Quiz finished, but failed to store score: {e}"
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail      = message
            )
    
    # Returning the score
    return ScoreResponse(username = _current_username, score = score * 10, message = message)

# Method to establish further questions
@router.get('/has_question', summary = 'Check if there are more questions')
async def check_has_question() -> dict:
    '''
    Checks if there are more questions available in the current quiz game.
    
    Input args:
    - None

    Return:
    - (dict) : Dictionary with has_more_questions attribute
    '''
    # Retrieving the game via helper
    game = get_current_game() 

    # Retruning a dictionary with errors
    return {"has_more_questions": game.has_question()}