# Import functionality from the FastAPI framework.
from fastapi import APIRouter, Depends

# Import our custom class for handling leaderboard logic.
from app.points.leaderboard import Leaderboard

# Create an instance of APIRouter.
router = APIRouter()

def get_leaderboard_service() -> Leaderboard:
    '''
    This is a dependency "stub". 
    
    The main application (`app.py`) will override this function to provide 
    the actual, initialized Leaderboard instance. This will raise an error
    if the main app forgets to do so.
    '''
    # This dependency will be overridden by the main application.
    raise NotImplementedError('get_leaderboard_service dependency must be overridden')

# The endpoint for retrieving the full leaderboard.
@router.get('/leaderboard')
def get_leaderboard_endpoint(
    leaderboard: Leaderboard = Depends(get_leaderboard_service)
):
    '''
    Retrieves the full leaderboard.

    Returns a list of all users, sorted from the highest total score to the lowest,
    with a detailed breakdown of their points.

    Input args:
    - leaderboard

    Return: 
    - list of messages
    '''
    # Use our leaderboard object to get the Scores collection.
    scores_collection = leaderboard.get_leaderboard()
    
    # Use the get_leaderboard method from the Scores object to get a sorted list.
    sorted_scores = scores_collection.get_leaderboard()
    
    # Convert the list of Score objects into a list of dictionaries for the JSON response.
    return [score.to_dict() for score in sorted_scores]

# The endpoint for retrieving a single user's score.
@router.get('/users/{username}/score')
def get_user_score_endpoint(
    username: str, leaderboard: Leaderboard = Depends(get_leaderboard_service)):
    '''
    Retrieves the detailed score breakdown for a specific user.

    Input args:
    - username (str)            : Username of user of interest
    - leaderboard (Leaderboard) : Leaderboard object to interact with db
    '''
    # Use our leaderboard object to get the Score object for the specified user.
    score_object = leaderboard.get_user_score(username=username)
    
    # Convert the Score object to a dictionary for the JSON response.
    return score_object.to_dict()