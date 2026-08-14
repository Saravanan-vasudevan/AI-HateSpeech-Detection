import unittest
from unittest.mock import MagicMock, patch

# Import the classes we are testing and their dependencies.
from app.points.leaderboard import Leaderboard
from app.utils.database import Database
from app.points.score import Score
from app.points.scores import Scores

# A test suite for the Leaderboard class.
class TestLeaderboard(unittest.TestCase):
    '''
    A test suite for the Leaderboard class, using a mock database
    to ensure the class is tested in isolation.
    '''
    # This method runs before each test.
    def setUp(self):
        '''
        Set up a mock Database object and an instance of the Leaderboard class.
        '''

        # Create a mock instance of the Database class.
        self.mock_db = MagicMock(spec=Database)

        # Create the Leaderboard instance, injecting the mock database.
        self.leaderboard = Leaderboard(self.mock_db)
        
    # A test for the initialization logic.
    def test_initialization_validation(self):
        '''
        Tests that the __init__ method raises a TypeError for invalid input.
        '''
        # Assert that passing something that isn't a Database object raises an error.
        with self.assertRaisesRegex(TypeError, 'must be an instance of the Database class'):
            Leaderboard(db_connection='not a valid database object')

    # A test for the main leaderboard generation logic.
    def test_get_leaderboard_combines_sources(self):
        '''
        Tests that get_leaderboard correctly fetches from both data sources,
        combines the scores, and returns a properly structured Scores object.
        '''
        # Arrange: Define the fake data our mock database will return.
        # This simulates users with scores in one, the other, or both collections.
        mock_prediction_scores = [
            {'_id': 'user_a', 'total_score': 100}, # Scores only in predictions
            {'_id': 'user_b', 'total_score': 20}   # Scores in both
        ]
        mock_quiz_scores = [
            {'_id': 'user_b', 'total_score': 30},  # Scores in both
            {'_id': 'user_c', 'total_score': 50}   # Scores only in quizzes
        ]

        # Configure the mock to return the correct data based on the collection name.
        # We use side_effect to return different values on subsequent calls.
        self.mock_db._get_collection.return_value.aggregate.side_effect = [
            mock_prediction_scores,
            mock_quiz_scores
        ]
        
        # Act: Call the method we are testing.
        scores_collection = self.leaderboard.get_leaderboard()
        
        # Assert: Check that the results are correct.
        # We expect 3 unique users in total.
        self.assertEqual(len(scores_collection), 3)
        
        # Get the sorted leaderboard to verify contents and totals.
        leaderboard_list = scores_collection.get_leaderboard()
        
        # Create a simple dictionary from the result for easier validation.
        results_map = {score.username: score.total_score for score in leaderboard_list}
        
        # Define the expected, correctly calculated totals.
        expected_totals = {
            'user_a': 100, # 100 from predictions + 0 from quizzes
            'user_b': 50,  # 20 from predictions + 30 from quizzes
            'user_c': 50   # 0 from predictions + 50 from quizzes
        }
        
        # Assert that the calculated totals match our expectations.
        self.assertDictEqual(results_map, expected_totals)

    # A test for handling database errors gracefully.
    def test_get_leaderboard_handles_db_error(self):
        '''
        Tests that get_leaderboard returns an empty Scores object if the
        database call fails.
        '''
        # Arrange: Configure the mock to raise an exception when called.
        self.mock_db._get_collection.return_value.aggregate.side_effect = Exception('Connection timed out')
        
        # Act: Call the method.
        scores_collection = self.leaderboard.get_leaderboard()
        
        # Assert: Ensure the result is an empty, but valid, Scores object.
        self.assertIsInstance(scores_collection, Scores)
        self.assertEqual(len(scores_collection), 0)

    # A test for getting a single user's score.
    def test_get_user_score(self):
        '''
        Tests that get_user_score correctly fetches and combines scores
        for a single specified user.
        '''
        # Arrange: Configure the mock database to return scores for 'test_user'.
        self.mock_db._get_collection.return_value.aggregate.side_effect = [
            [{'_id': 'test_user', 'total_score': 70}], # Mock predictions
            [{'_id': 'test_user', 'total_score': 25}]  # Mock quizzes
        ]
        
        # Act: Get the score for 'test_user'.
        user_score = self.leaderboard.get_user_score(username = 'test_user')
        
        # Assert: Check that the returned Score object has the correct values.
        self.assertEqual(user_score.prediction_score, 70)
        self.assertEqual(user_score.quiz_score, 25)
        self.assertEqual(user_score.total_score, 95)

# This allows the test to be run from the command line.
if __name__ == '__main__':
    unittest.main()