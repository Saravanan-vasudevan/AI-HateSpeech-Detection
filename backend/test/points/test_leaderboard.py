import unittest
from unittest.mock import MagicMock, patch

from app.points.leaderboard import Leaderboard
from app.utils.database import Database
from app.points.score import Score
from app.points.scores import Scores

class TestLeaderboard(unittest.TestCase):
    def setUp(self):

        self.mock_db = MagicMock(spec=Database)

        self.leaderboard = Leaderboard(self.mock_db)

    def test_initialization_validation(self):
        with self.assertRaisesRegex(TypeError, 'must be an instance of the Database class'):
            Leaderboard(db_connection='not a valid database object')

    def test_get_leaderboard_combines_sources(self):
        mock_prediction_scores = [
            {'_id': 'user_a', 'total_score': 100},
            {'_id': 'user_b', 'total_score': 20}
        ]
        mock_quiz_scores = [
            {'_id': 'user_b', 'total_score': 30},
            {'_id': 'user_c', 'total_score': 50}
        ]

        self.mock_db._get_collection.return_value.aggregate.side_effect = [
            mock_prediction_scores,
            mock_quiz_scores
        ]

        scores_collection = self.leaderboard.get_leaderboard()

        self.assertEqual(len(scores_collection), 3)

        leaderboard_list = scores_collection.get_leaderboard()

        results_map = {score.username: score.total_score for score in leaderboard_list}

        expected_totals = {
            'user_a': 100,
            'user_b': 50,
            'user_c': 50
        }

        self.assertDictEqual(results_map, expected_totals)

    def test_get_leaderboard_handles_db_error(self):
        self.mock_db._get_collection.return_value.aggregate.side_effect = Exception('Connection timed out')

        scores_collection = self.leaderboard.get_leaderboard()

        self.assertIsInstance(scores_collection, Scores)
        self.assertEqual(len(scores_collection), 0)

    def test_get_user_score(self):
        self.mock_db._get_collection.return_value.aggregate.side_effect = [
            [{'_id': 'test_user', 'total_score': 70}],
            [{'_id': 'test_user', 'total_score': 25}]
        ]

        user_score = self.leaderboard.get_user_score(username = 'test_user')

        self.assertEqual(user_score.prediction_score, 70)
        self.assertEqual(user_score.quiz_score, 25)
        self.assertEqual(user_score.total_score, 95)

if __name__ == '__main__':
    unittest.main()