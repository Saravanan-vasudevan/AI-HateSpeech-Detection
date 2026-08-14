import unittest
import datetime
from unittest.mock import MagicMock, patch
from fastapi import status
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the code to be tested
from app.history.api import router, set_history_manager, get_current_user
from app.history.history import History
from app.history.predictions import Predictions
from app.history.prediction import Prediction
from app.utils.user import User

# Creating a test application along with router
test_app = FastAPI()
test_app.include_router(router, prefix='/history') 

# Mock user
# - This is needed for authentication
mock_user = User(username = 'test_user', first_name = 'Test', 
                 last_name = 'User', admin = False)

def override_get_current_user():
    '''
    A dependency override that returns a mock user.
    '''
    # Returning our mock user
    return mock_user

# Apply the dependency override to the test app
test_app.dependency_overrides[get_current_user] = override_get_current_user


class TestHistoryAPI(unittest.TestCase):
    '''
    Unit tests for the history/api.py FastAPI router.
    '''

    def setUp(self):
        '''
        Set up a mock History manager and a TestClient for each test.
        '''
        # Creating our mock history manager
        self.mock_history_manager = MagicMock(spec = History)
        set_history_manager(self.mock_history_manager)

        # Creating a client
        # - This is using our app / router
        self.client = TestClient(test_app)

        # UPDATED: Sample Prediction objects now include all required fields
        self.pred1 = Prediction('test_user', '2025-07-01T10:00:00Z', 'Text A', True, True, 'h_expl_A', 'a_expl_A', 0.9)
        self.pred2 = Prediction('test_user', '2025-07-05T11:00:00Z', 'Text B', False, True, 'h_expl_B', 'a_expl_B', 0.8)

    def tearDown(self):
        '''
        Clean up by resetting the history manager after each test.
        '''
        # Clearing the history manager
        set_history_manager(None)



    def test_get_predictions_success(self):
        '''
        Test retrieving all predictions successfully for the authenticated user.
        '''
        # Specifying what our historyh will return (2 predictions)
        mock_predictions = Predictions(initial_predictions = [self.pred2, self.pred1])

        # Perofmring the retieval
        self.mock_history_manager.retrieve_predictions.return_value = mock_predictions

        # Using API end-point to get data
        response = self.client.get('/history/')
        
        # Check - Was a valid response returned?
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check - Were 2 records returned?
        response_data = response.json()
        self.assertEqual(len(response_data), 2)

        # Check that the data matches what Prediction.get() returns
        self.assertEqual(response_data[0]['text'], self.pred2.get()['text'])
        self.assertEqual(response_data[1]['text'], self.pred1.get()['text'])

        # Check that the manager was called correctly for the authenticated user
        self.mock_history_manager.retrieve_predictions.assert_called_once_with(
            username=mock_user.get_username(), limit=100  # Note the new default limit
        )

    def test_get_predictions_with_limit(self):
        '''
        Test retrieving a limited number of predictions.
        '''
        # Specifying we will return a single record this ti,e
        mock_predictions = Predictions(initial_predictions=[self.pred2])
        self.mock_history_manager.retrieve_predictions.return_value = mock_predictions

        # Using API to get records
        response = self.client.get('/history/?limit=1')
        
        # Check - Was a valid response produced?
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check - Was 1 record returned?
        self.assertEqual(len(response.json()), 1)

        # Check - Did we call the retrieve predictions once?
        self.mock_history_manager.retrieve_predictions.assert_called_once_with(
            username = mock_user.get_username(), limit = 1
        )

    def test_add_prediction_success(self):
        '''
        Test logging a new prediction successfully.
        '''
        # JSON to log
        request_data = {
            'text'             : 'A new prediction to log.',
            'human_prediction' : True,
            'ai_prediction'    : False,
            'human_explanation': 'Because I said so.',
            'ai_explanation'   : 'Model says no.',
            'probability'      : 0.45
        }
        
        # Configure the mock to return a fake database ID
        self.mock_history_manager.log_prediction.return_value = "fake_mongo_id_123"

        # Positng our mock data
        response = self.client.post('/history/', json=request_data)

        # Check for 201 Created status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {'status': 'success', 'inserted_id': 'fake_mongo_id_123'})

        # Verify that the manager's log_prediction method was called with the correct data
        self.mock_history_manager.log_prediction.assert_called_once_with(
            username          = mock_user.get_username(),
            text              = request_data['text'],
            human             = request_data['human_prediction'],
            ai                = request_data['ai_prediction'],
            human_explanation = request_data['human_explanation'],
            ai_explanation    =  request_data['ai_explanation'],
            p                 =request_data['probability']
        )

    def test_add_prediction_invalid_data(self):
        '''
        Test that logging a prediction with invalid data fails with a 422 error.
        '''
        # Creating invalid request
        # N.B - Probability is wrong
        invalid_request_data = {
            'text'             : 'Invalid data', 
            'human_prediction' : True, 
            'ai_prediction'    : False,
            'human_explanation': 'h', 
            'ai_explanation'   : 'a', 
            'probability'      : 1.5
        }
        # Posting the data to mock client
        response = self.client.post('/history/', json=invalid_request_data)

        # Check - Failed with Pydantic errors
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY) 
        
        # Check that the log method was never called
        self.mock_history_manager.log_prediction.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)