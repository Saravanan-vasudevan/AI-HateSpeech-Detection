import unittest
import datetime
from unittest.mock import MagicMock, patch
from app.history.predictions import Predictions
from app.utils.database import Database
from app.history.history import History

class TestHistory(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock(spec = Database)

        self.mock_collection = MagicMock()
        self.mock_db._get_collection.return_value = self.mock_collection

        self.collection_name = 'test_predictions'

        self.history_instance = History(
            db_connection   = self.mock_db,
            collection_name = self.collection_name
        )

        self.raw_record1 = {
            '_id'              : 'rec1',
            'username'         : 'userA',
            'text'             : 'Hello world.',
            'timestamp'        : datetime.datetime(2025, 7, 1, 10, 0, 0),
            'human'            : True,
            'ai'               : True,
            'score'            : 10,
            'human_explanation': 'h_expl_1',
            'ai_explanation'   : 'a_expl_1',
            'p'                : 0.9
        }
        self.raw_record2 = {
            '_id'              : 'rec2',
            'username'         : 'userB',
            'text'             : 'Another text.',
            'timestamp'        : datetime.datetime(2025, 7, 5, 12, 30, 0),
            'human'            : False,
            'ai'               : True,
            'score'            : 0,
            'human_explanation': 'h_expl_2',
            'ai_explanation'   : 'a_expl_2',
            'p'                : 0.8
        }

    def test_history_initialization_valid(self):
        self.assertIsInstance(self.history_instance, History)

        self.mock_db._get_collection.assert_called_once_with(self.collection_name)

    def test_retrieve_predictions_all_records(self):
        self.mock_db.get_records.return_value = [self.raw_record2, self.raw_record1]

        predictions_collection = self.history_instance.retrieve_predictions()

        self.assertIsInstance(predictions_collection, Predictions)

        self.assertEqual(len(predictions_collection), 2)

        self.mock_db.get_records.assert_called_once_with(
            collection_name = self.collection_name,
            query           = {},
            limit           = 0,
            sort            = [('timestamp', -1)]
        )

    def test_retrieve_predictions_with_username_filter(self):
        self.mock_db.get_records.return_value = [self.raw_record1]

        predictions_collection = self.history_instance.retrieve_predictions(username='userA')

        self.assertEqual(len(predictions_collection), 1)

        self.assertEqual(predictions_collection[0]._username, 'userA')

        self.mock_db.get_records.assert_called_once_with(
            collection_name = self.collection_name,
            query           = {'username': 'userA'},
            limit           = 0,
            sort            = [('timestamp', -1)]
        )

    def test_retrieve_predictions_malformed_record_is_skipped(self):
        malformed_record = {
            '_id'       : 'malformed',
            'username'  : 'userX',
            'text'      : 'Bad data record.',
            'timestamp' : datetime.datetime.now(),
            'human'     : 'not-a-boolean'
        }
        self.mock_db.get_records.return_value = [self.raw_record2, malformed_record]

        with patch('builtins.print') as mock_print:
            predictions_collection = self.history_instance.retrieve_predictions()

            self.assertEqual(len(predictions_collection), 1)

            mock_print.assert_called()

    def test_log_prediction(self):
        log_args = {
            'username'         : 'new_user',
            'text'             : 'new text',
            'human'            : True,
            'ai'               : False,
            'human_explanation': 'new h_expl',
            'ai_explanation'   : 'new a_expl',
            'p'                : 0.4
        }

        self.history_instance.log_prediction(**log_args)

        self.mock_collection.insert_one.assert_called_once()

        inserted_data = self.mock_collection.insert_one.call_args[0][0]

        self.assertEqual(inserted_data['username'], 'new_user')
        self.assertEqual(inserted_data['p'], 0.4)
        self.assertEqual(inserted_data['score'], 0)
        self.assertIn('timestamp', inserted_data)
        self.assertIsInstance(inserted_data['timestamp'], datetime.datetime)

if __name__ == '__main__':

    unittest.main(argv = ['first-arg-is-ignored'], exit = False)