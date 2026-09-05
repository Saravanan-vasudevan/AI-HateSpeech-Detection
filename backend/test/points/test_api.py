import unittest
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.points.api import router as api_router
from app.points.api import get_leaderboard_service

from app.points.leaderboard import Leaderboard
from app.points.score import Score
from app.points.scores import Scores


mock_leaderboard_service = MagicMock(spec=Leaderboard)

app = FastAPI()

app.dependency_overrides[get_leaderboard_service] = lambda: mock_leaderboard_service

app.include_router(api_router)

client = TestClient(app)


class TestApi(unittest.TestCase):

    def test_get_leaderboard_endpoint(self):
        expected_data = [
            {'username': 'user_a', 'prediction_score': 100, 'quiz_score': 0, 'total_score': 100},
            {'username': 'user_b', 'prediction_score': 50, 'quiz_score': 25, 'total_score': 75}
        ]

        mock_score_a = MagicMock(spec=Score)
        mock_score_a.to_dict.return_value = expected_data[0]

        mock_score_b = MagicMock(spec=Score)
        mock_score_b.to_dict.return_value = expected_data[1]

        mock_scores_collection = MagicMock(spec=Scores)
        mock_scores_collection.get_leaderboard.return_value = [mock_score_a, mock_score_b]
        mock_leaderboard_service.get_leaderboard.return_value = mock_scores_collection

        response = client.get('/leaderboard')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_get_user_score_endpoint(self):
        username = 'test_user'
        expected_data = {
            'username': username,
            'prediction_score': 50,
            'quiz_score': 20,
            'total_score': 70
        }

        mock_leaderboard_service.get_user_score.return_value.to_dict.return_value = expected_data

        response = client.get(f'/users/{username}/score')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        mock_leaderboard_service.get_user_score.assert_called_with(username=username)

if __name__ == '__main__':
    unittest.main()