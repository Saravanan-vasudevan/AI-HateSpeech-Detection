from fastapi import APIRouter, Depends

from app.points.leaderboard import Leaderboard

router = APIRouter()

def get_leaderboard_service() -> Leaderboard:
    '''
    This is a dependency "stub".

    The main application (`app.py`) will override this function to provide
    the actual, initialized Leaderboard instance. This will raise an error
    if the main app forgets to do so.
    '''
    raise NotImplementedError('get_leaderboard_service dependency must be overridden')

@router.get('/leaderboard')
def get_leaderboard_endpoint(
    leaderboard: Leaderboard = Depends(get_leaderboard_service)
):
    scores_collection = leaderboard.get_leaderboard()

    sorted_scores = scores_collection.get_leaderboard()

    return [score.to_dict() for score in sorted_scores]

@router.get('/users/{username}/score')
def get_user_score_endpoint(
    username: str, leaderboard: Leaderboard = Depends(get_leaderboard_service)):
    score_object = leaderboard.get_user_score(username=username)

    return score_object.to_dict()