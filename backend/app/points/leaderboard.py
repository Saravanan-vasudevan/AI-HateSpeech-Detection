from app.utils.database import Database
from app.points.score import Score
from app.points.scores import Scores

class Leaderboard:
    '''
    Handles the logic for fetching and calculating scores from the database.

    This class uses a Database connection to query different collections,
    aggregate points for users, and build Score and Scores objects.
    '''
    def __init__(self, db_connection: Database):
        '''
        Initializes the Leaderboard with a database connection.

        Args:
        - db_connection (Database): An active instance of the Database class.

        Raises:
        - TypeError: If db_connection is not an instance of the Database class.
        '''
        if not isinstance(db_connection, Database):
            raise TypeError('db_connection must be an instance of the Database class.')

        self._db = db_connection

        self._predictions_coll_name = 'predictions'
        self._quiz_coll_name        = 'quiz_scores'

    def _aggregate_scores_by_user(self, collection_name: str) -> dict:
        '''
        Aggregates the total score for each user in a given collection.

        Args:
        - collection_name (str): The name of the collection to query.

        Returns:
        - dict: A dictionary mapping each username to their total score.
                Returns an empty dictionary if the operation fails.
        '''
        collection = self._db._get_collection(collection_name)

        if collection is None:
            return {}

        pipeline = [
            { '$match': { 'username': { '$type': 'string', '$ne': '' } } },
            { '$group': { '_id': '$username', 'total_score': { '$sum': '$score' } } }
        ]

        try:
            results = collection.aggregate(pipeline)

            return {item['_id']: item['total_score'] for item in results}

        except Exception as e:

            print(f'An error occurred during aggregation on {collection_name}: {e}')
            return {}

    def get_leaderboard(self) -> Scores:
        '''
        Fetches scores from all sources and compiles them into a Scores object.

        Returns:
        - Scores: A Scores object containing Score objects for every user
                  who has earned points.
        '''
        prediction_scores = self._aggregate_scores_by_user(self._predictions_coll_name)
        quiz_scores       = self._aggregate_scores_by_user(self._quiz_coll_name)

        all_usernames = set(prediction_scores.keys()) | set(quiz_scores.keys())

        score_objects = []

        for username in all_usernames:

            pred_score = prediction_scores.get(username, 0)
            q_score   = quiz_scores.get(username, 0)

            score_objects.append(Score(username, pred_score, q_score))

        return Scores(initial_scores=score_objects)

    def get_user_score(self, username: str) -> Score:
        '''
        Fetches and calculates the total score for a single specified user.

        Args:
        - username (str): The username to look up.

        Returns:
        = Score: A Score object containing the user's detailed points.
        '''

        prediction_scores = self._aggregate_scores_by_user(self._predictions_coll_name)
        quiz_scores       = self._aggregate_scores_by_user(self._quiz_coll_name)

        user_pred_score = prediction_scores.get(username, 0)
        user_quiz_score = quiz_scores.get(username, 0)

        return Score(username, user_pred_score, user_quiz_score)