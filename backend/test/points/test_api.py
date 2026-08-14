import unittest
from unittest.mock import MagicMock

# Import the testing tools from FastAPI.
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import the router and dependency stub from our api.py file.
from app.points.api import router as api_router
from app.points.api import get_leaderboard_service

# Import the classes we will need to mock.
from app.points.leaderboard import Leaderboard
from app.points.score import Score
from app.points.scores import Scores

# --- Test Setup ---

# 1. Create a mock leaderboard service.
# This object will imitate our real Leaderboard class.
mock_leaderboard_service = MagicMock(spec=Leaderboard)

# 2. Create a minimal FastAPI application for testing.
app = FastAPI()

# 3. Override the dependency.
app.dependency_overrides[get_leaderboard_service] = lambda: mock_leaderboard_service

# 4. Include the API router in our test app.
app.include_router(api_router)

# 5. Create the TestClient.
# This client will make requests to our test app.
client = TestClient(app)

# --- Test Cases ---

# A test suite for the API endpoints.
class TestApi(unittest.TestCase):
    '''
    A test suite for the API router, ensuring endpoints respond correctly.
    '''

    # A test for the /leaderboard endpoint.
    def test_get_leaderboard_endpoint(self):
        '''
        Tests the /leaderboard endpoint for a successful response.
        '''
        # Arrange: Define the fake data the mock service should return.
        expected_data = [
            {'username': 'user_a', 'prediction_score': 100, 'quiz_score': 0, 'total_score': 100},
            {'username': 'user_b', 'prediction_score': 50, 'quiz_score': 25, 'total_score': 75}
        ]
        
        # Create mock Score objects that will be returned by the service.
        mock_score_a = MagicMock(spec=Score)
        mock_score_a.to_dict.return_value = expected_data[0]
        
        mock_score_b = MagicMock(spec=Score)
        mock_score_b.to_dict.return_value = expected_data[1]
        
        # Configure the full chain of mock calls.
        mock_scores_collection = MagicMock(spec=Scores)
        mock_scores_collection.get_leaderboard.return_value = [mock_score_a, mock_score_b]
        mock_leaderboard_service.get_leaderboard.return_value = mock_scores_collection
        
        # Act: Make a GET request to the endpoint.
        response = client.get('/leaderboard')
        
        # Assert: Check the status code and the JSON response body.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    # A test for the /users/{username}/score endpoint.
    def test_get_user_score_endpoint(self):
        '''
        Tests the /users/{username}/score endpoint for a successful response.
        '''
        # Arrange: Define the fake data for a single user.
        username = 'test_user'
        expected_data = {
            'username': username,
            'prediction_score': 50,
            'quiz_score': 20,
            'total_score': 70
        }
        
        # Configure the mock to return an object that has a .to_dict() method.
        mock_leaderboard_service.get_user_score.return_value.to_dict.return_value = expected_data
        
        # Act: Make a GET request to the endpoint with a specific username.
        response = client.get(f'/users/{username}/score')
        
        # Assert: Check the status code and the response body.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)
        
        # Assert that our mock service was called correctly.
        mock_leaderboard_service.get_user_score.assert_called_with(username=username)

# This allows the test to be run from the command line.
if __name__ == '__main__':
    unittest.main()