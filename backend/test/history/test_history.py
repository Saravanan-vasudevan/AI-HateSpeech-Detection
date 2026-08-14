import unittest
import datetime
from unittest.mock import MagicMock, patch
from app.history.predictions import Predictions
from app.utils.database import Database
from app.history.history import History

class TestHistory(unittest.TestCase):
    '''
    Unit tests for the History class, using a mocked database.
    '''

    def setUp(self):
        '''
        Set up a mock Database object and a History instance for each test.
        '''
        # A mocking database object
        self.mock_db = MagicMock(spec = Database)

        # Configure the mock to return another mock for the collection object
        self.mock_collection = MagicMock()
        self.mock_db._get_collection.return_value = self.mock_collection
        
        # Specifying the name of the collection where data is stored
        self.collection_name = 'test_predictions'

        # Creating a history object
        # - This should use our mock objects
        self.history_instance = History(
            db_connection   = self.mock_db,
            collection_name = self.collection_name
        )

        # Creating two records
        # - This are correct and have the right values
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
        '''
        Test that History initializes correctly with valid inputs.
        '''
        # Check - is our history of the correct type?
        self.assertIsInstance(self.history_instance, History)

        # Check - Was the collection called once with the right name?
        self.mock_db._get_collection.assert_called_once_with(self.collection_name)

    def test_retrieve_predictions_all_records(self):
        '''
        Test retrieving all predictions without any filters.
        '''
        # Specifying what the get_records method will return
        self.mock_db.get_records.return_value = [self.raw_record2, self.raw_record1]
        
        # Retrieving the records we have specified
        predictions_collection = self.history_instance.retrieve_predictions()

        # Check - Were predictions returned?
        self.assertIsInstance(predictions_collection, Predictions)

        # Were two predictions returned?
        self.assertEqual(len(predictions_collection), 2)
        
        # Check - Were get records called once (no query)
        self.mock_db.get_records.assert_called_once_with(
            collection_name = self.collection_name,
            query           = {},
            limit           = 0,
            sort            = [('timestamp', -1)]
        )

    def test_retrieve_predictions_with_username_filter(self):
        '''
        Test retrieving predictions filtered by a specific username.
        '''
        # Specifying 1 record is returned this time
        self.mock_db.get_records.return_value = [self.raw_record1]
        
        # Retrieving our records using the mock db
        predictions_collection = self.history_instance.retrieve_predictions(username='userA')

        # Check - Was one record actually returned?
        self.assertEqual(len(predictions_collection), 1)

        # Check - Is the username returned of the correct type?
        self.assertEqual(predictions_collection[0]._username, 'userA')

        # Check - Was get records called with correct inputs?
        self.mock_db.get_records.assert_called_once_with(
            collection_name = self.collection_name,
            query           = {'username': 'userA'},
            limit           = 0,
            sort            = [('timestamp', -1)]
        )

    def test_retrieve_predictions_malformed_record_is_skipped(self):
        '''
        Test that malformed records from the database are skipped gracefully.
        '''
        # This record is malformed because 'timestamp' is missing, which Prediction() requires.
        malformed_record = {
            '_id'       : 'malformed',
            'username'  : 'userX',
            'text'      : 'Bad data record.',
            'timestamp' : datetime.datetime.now(),
            'human'     : 'not-a-boolean' 
        }
        # Specifying the db will return a mock records
        self.mock_db.get_records.return_value = [self.raw_record2, malformed_record]
        
        with patch('builtins.print') as mock_print:
            predictions_collection = self.history_instance.retrieve_predictions()
            
            # Check - Was one valid record called? 
            self.assertEqual(len(predictions_collection), 1)

            # Check that an error message was printed for the skipped record
            mock_print.assert_called()

    def test_log_prediction(self):
        '''
        Tests that the log_prediction method constructs the correct data
        dictionary and calls the database insert method.
        '''
        # Record that we are going to log to db
        log_args = {
            'username'         : 'new_user', 
            'text'             : 'new text', 
            'human'            : True, 
            'ai'               : False,
            'human_explanation': 'new h_expl', 
            'ai_explanation'   : 'new a_expl', 
            'p'                : 0.4
        }

        # Performing the lock
        self.history_instance.log_prediction(**log_args)

        # Check that insert_one was called on our mock collection
        self.mock_collection.insert_one.assert_called_once()
        
        # Get the dictionary that was passed to insert_one
        inserted_data = self.mock_collection.insert_one.call_args[0][0]
        
        # Verify the contents of the dictionary
        self.assertEqual(inserted_data['username'], 'new_user')
        self.assertEqual(inserted_data['p'], 0.4)
        self.assertEqual(inserted_data['score'], 0)
        self.assertIn('timestamp', inserted_data)
        self.assertIsInstance(inserted_data['timestamp'], datetime.datetime)

if __name__ == '__main__':

    unittest.main(argv = ['first-arg-is-ignored'], exit = False)