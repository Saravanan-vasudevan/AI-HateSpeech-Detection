import unittest
import datetime
from unittest.mock import MagicMock, patch
from fastapi import status
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.history.api import router, set_history_manager, get_current_user
from app.history.history import History
from app.history.predictions import Predictions
from app.history.prediction import Prediction
from app.utils.user import User

test_app = FastAPI()
test_app.include_router(router, prefix='/history')

mock_user = User(username = 'test_user', first_name = 'Test',
                 last_name = 'User', admin = False)

def override_get_current_user():
    return mock_user

test_app.dependency_overrides[get_current_user] = override_get_current_user


class TestHistoryAPI(unittest.TestCase):

    def setUp(self):
        self.mock_history_manager = MagicMock(spec = History)
        set_history_manager(self.mock_history_manager)

        self.client = TestClient(test_app)

        self.pred1 = Prediction('test_user', '2025-07-01T10:00:00Z', 'Text A', True, True, 'h_expl_A', 'a_expl_A', 0.9)
        self.pred2 = Prediction('test_user', '2025-07-05T11:00:00Z', 'Text B', False, True, 'h_expl_B', 'a_expl_B', 0.8)

    def tearDown(self):
        set_history_manager(None)



    def test_get_predictions_success(self):
        mock_predictions = Predictions(initial_predictions = [self.pred2, self.pred1])

        self.mock_history_manager.retrieve_predictions.return_value = mock_predictions

        response = self.client.get('/history/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(len(response_data), 2)

        self.assertEqual(response_data[0]['text'], self.pred2.get()['text'])
        self.assertEqual(response_data[1]['text'], self.pred1.get()['text'])

        self.mock_history_manager.retrieve_predictions.assert_called_once_with(
            username=mock_user.get_username(), limit=100
        )

    def test_get_predictions_with_limit(self):
        mock_predictions = Predictions(initial_predictions=[self.pred2])
        self.mock_history_manager.retrieve_predictions.return_value = mock_predictions

        response = self.client.get('/history/?limit=1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()), 1)

        self.mock_history_manager.retrieve_predictions.assert_called_once_with(
            username = mock_user.get_username(), limit = 1
        )

    def test_add_prediction_success(self):
        request_data = {
            'text'             : 'A new prediction to log.',
            'human_prediction' : True,
            'ai_prediction'    : False,
            'human_explanation': 'Because I said so.',
            'ai_explanation'   : 'Model says no.',
            'probability'      : 0.45
        }

        self.mock_history_manager.log_prediction.return_value = "fake_mongo_id_123"

        response = self.client.post('/history/', json=request_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {'status': 'success', 'inserted_id': 'fake_mongo_id_123'})

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
        invalid_request_data = {
            'text'             : 'Invalid data',
            'human_prediction' : True,
            'ai_prediction'    : False,
            'human_explanation': 'h',
            'ai_explanation'   : 'a',
            'probability'      : 1.5
        }
        response = self.client.post('/history/', json=invalid_request_data)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        self.mock_history_manager.log_prediction.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)