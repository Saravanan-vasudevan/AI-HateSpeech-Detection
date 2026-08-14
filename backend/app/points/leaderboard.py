from app.utils.database import Database
from app.points.score import Score
from app.points.scores import Scores

# A class to interact with the database to generate scores and leaderboards.
class Leaderboard:
    '''
    Handles the logic for fetching and calculating scores from the database.

    This class uses a Database connection to query different collections,
    aggregate points for users, and build Score and Scores objects.
    '''
    # Initializes a new Leaderboard instance.
    def __init__(self, db_connection: Database):
        '''
        Initializes the Leaderboard with a database connection.

        Args:
        - db_connection (Database): An active instance of the Database class.

        Raises:
        - TypeError: If db_connection is not an instance of the Database class.
        '''
        # Validate that we have a proper Database object.
        if not isinstance(db_connection, Database):
            raise TypeError('db_connection must be an instance of the Database class.')
        
        # Store the database connection.
        self._db = db_connection
        
        # Define the names of the collections we will be working with.
        self._predictions_coll_name = 'predictions'
        self._quiz_coll_name        = 'quiz_scores'

    # A private helper method to run an aggregation query and return scores.
    def _aggregate_scores_by_user(self, collection_name: str) -> dict:
        '''
        Aggregates the total score for each user in a given collection.

        Args:
        - collection_name (str): The name of the collection to query.

        Returns:
        - dict: A dictionary mapping each username to their total score.
                Returns an empty dictionary if the operation fails.
        '''
        # Retrieve the collection object from our database instance.
        collection = self._db._get_collection(collection_name)
        
        # If the collection doesn't exist or we can't connect, return empty.
        if collection is None:
            return {}

        # Define the aggregation pipeline to group by username and sum scores.
        pipeline = [
            { '$match': { 'username': { '$type': 'string', '$ne': '' } } },
            { '$group': { '_id': '$username', 'total_score': { '$sum': '$score' } } }
        ]
        
        try:
            # Execute the aggregation query.
            results = collection.aggregate(pipeline)

            # Convert the cursor result into a user-friendly dictionary.
            return {item['_id']: item['total_score'] for item in results}
        
        except Exception as e:

            # If anything goes wrong, log the error and return an empty dict.
            print(f'An error occurred during aggregation on {collection_name}: {e}')
            return {}

    # The main method to generate the full leaderboard.
    def get_leaderboard(self) -> Scores:
        '''
        Fetches scores from all sources and compiles them into a Scores object.

        Returns:
        - Scores: A Scores object containing Score objects for every user
                  who has earned points.
        '''
        # Get the aggregated scores from both sources.
        prediction_scores = self._aggregate_scores_by_user(self._predictions_coll_name)
        quiz_scores       = self._aggregate_scores_by_user(self._quiz_coll_name)
        
        # Get a unique set of all usernames from both dictionaries.
        all_usernames = set(prediction_scores.keys()) | set(quiz_scores.keys())
        
        # A list to hold the individual Score objects we create.
        score_objects = []
        
        # Iterate through each unique username to build their complete score.
        for username in all_usernames:

            # Get the score from each source, defaulting to 0 if the user has no score.
            pred_score = prediction_scores.get(username, 0)
            q_score   = quiz_scores.get(username, 0)
            
            # Create a Score object and add it to our list.
            score_objects.append(Score(username, pred_score, q_score))
            
        # Create and return a Scores collection from our list of objects.
        return Scores(initial_scores=score_objects)

    # A method to get the detailed score for a single user.
    def get_user_score(self, username: str) -> Score:
        '''
        Fetches and calculates the total score for a single specified user.

        Args:
        - username (str): The username to look up.

        Returns:
        = Score: A Score object containing the user's detailed points.
        '''
        
        # Use the aggregation helper to get all scores.
        # This is simpler than creating a new, specific aggregation for one user.
        prediction_scores = self._aggregate_scores_by_user(self._predictions_coll_name)
        quiz_scores       = self._aggregate_scores_by_user(self._quiz_coll_name)
        
        # Get the specific user's score, defaulting to 0.
        user_pred_score = prediction_scores.get(username, 0)
        user_quiz_score = quiz_scores.get(username, 0)
        
        # Create and return the Score object for this user.
        return Score(username, user_pred_score, user_quiz_score)