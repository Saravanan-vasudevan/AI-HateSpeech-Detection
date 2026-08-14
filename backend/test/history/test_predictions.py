import unittest
import datetime
from dateutil.parser import parse as dateutil_parse
from app.history.prediction import Prediction
from app.history.predictions import Predictions

class TestPredictions(unittest.TestCase):
    '''
    Unit tests for the Predictions class.
    '''

    def setUp(self):
        '''
        Set up common Prediction objects for tests.
        '''
        # Creating four predictions for purpose of our testing
        self.pred1 = Prediction('u1', '2024-01-01 10:00:00', 'text1', True, True)
        self.pred2 = Prediction('u2', '2024-01-05 11:00:00', 'text2', False, True)
        self.pred3 = Prediction('u3', '2024-01-03 12:00:00', 'text3', True, False) 
        self.pred4 = Prediction('u4', '2024-01-07 13:00:00', 'text4', False, False) 

    def test_predictions_initialization_empty(self):
        '''
        Test initialization with no initial predictions.
        '''
        # Test 1 - Creating a predictions object (but with predictions supply)
        preds = Predictions()

        # Check - Does it actually exist as predictions object?
        self.assertIsInstance(preds, Predictions)

        # Check - Is the underlying predictions equal to 0?
        self.assertEqual(len(preds), 0)

    def test_predictions_initialization_with_list(self):
        '''
        Test initialization with a valid list of Prediction objects.
        '''
        # Creating a list of 2 predictions
        initial_list = [self.pred1, self.pred2]

        # Creating our predictions object
        preds = Predictions(initial_predictions=initial_list)

        # Check - Does our object have two predictions?
        self.assertEqual(len(preds), 2)

        # Check - Is our first prediction stored? 
        self.assertIn(self.pred1, preds._predictions)

        # Check - Os our second prediction stored?
        self.assertIn(self.pred2, preds._predictions)

    def test_predictions_initialization_with_non_list(self):
        '''
        Test initialization with a non-list object.
        '''
        # Check - Does it identify non-list arguments?
        with self.assertRaisesRegex(TypeError, 'Initial_predictions must be a list of Prediction objects.'):
            Predictions(initial_predictions = 'not a list')

    def test_predictions_initialization_with_list_containing_non_prediction(self):
        '''
        Test initialization with a list containing non-Prediction objects.
        '''
        # Check - A mix. A list of predictions where some are / aren't predictions
        initial_list = [self.pred1, 'not a prediction']
        with self.assertRaisesRegex(TypeError, "Only instances of 'Prediction' can be added."):
            Predictions(initial_predictions=initial_list)

    def test_add_prediction_valid(self):
        '''
        Test adding a single valid Prediction.
        '''
        # Setting up a predictions with no actual predictions
        preds = Predictions()

        # Check - Does it identify that no predictions included?
        self.assertEqual(len(preds), 0)

        # Check - Adding a prediction and checking length is 1?
        preds.add_prediction(self.pred1)
        self.assertEqual(len(preds), 1)

        # Check - Is our prediction in the predictions object?
        self.assertIn(self.pred1, preds._predictions)

    def test_add_prediction_invalid_type(self):
        '''
        Test adding an object that is not a Prediction.
        '''
        # Creating an empty predictions object
        preds = Predictions()

        # Check - Does it raise an exeption when I add a new prediction object?
        with self.assertRaisesRegex(TypeError, "Only instances of 'Prediction' can be added."):
            preds.add_prediction('not a prediction object')

    def test_get_n_predictions_all(self):
        '''
        Test getting all predictions when n is greater than total.
        '''
        # Passing all 4 predictions
        preds = Predictions(initial_predictions=[self.pred1, self.pred2, self.pred3, self.pred4])

        # Trying to retrieve 5 predictions
        # Check - Does it only actually return 4?
        result = preds.get_n_predictions(5) 
        self.assertEqual(len(result), 4)
        
        # Verify descending order
        self.assertEqual(result[0], self.pred4) # Most recent
        self.assertEqual(result[1], self.pred2)
        self.assertEqual(result[2], self.pred3)
        self.assertEqual(result[3], self.pred1) # Least recent

    def test_get_n_predictions_subset(self):
        '''
        Test getting a subset of predictions.
        '''
        # Putting our 4 predictions in the object
        preds = Predictions(initial_predictions=[self.pred1, self.pred2, self.pred3, self.pred4])

        # Retrieving two items and checking length is 2
        result = preds.get_n_predictions(2)
        self.assertEqual(len(result), 2)

        # Check - Are the two most recent predictions actually there?
        self.assertEqual(result[0], self.pred4)
        self.assertEqual(result[1], self.pred2)

    def test_get_n_predictions_empty_collection(self):
        '''
        Test getting predictions from an empty collection.
        '''
        # Creating no actual predictions
        preds = Predictions()
        result = preds.get_n_predictions(1)

        # Check - Are no actually returned?
        self.assertEqual(len(result), 0)

        # Check - Is what's returned an empty list?
        self.assertEqual(result, [])

    def test_get_n_predictions_n_equals_zero(self):
        '''
        Test get_n_predictions with n=0 (should raise ValueError).
        '''
        preds = Predictions([self.pred1])
        with self.assertRaisesRegex(ValueError, 'The number of predictions \'n\' must be a positive integer.'):
            preds.get_n_predictions(0)

    def test_get_n_predictions_n_negative(self):
        '''
        Test get_n_predictions with n negative (should raise ValueError).
        '''
        # Passing a single prediction
        preds = Predictions([self.pred1])

        # Check - Does it pick up an error with negative predictions?
        with self.assertRaisesRegex(ValueError, 'The number of predictions \'n\' must be a positive integer.'):
            preds.get_n_predictions(-1)

    def test_get_n_predictions_n_non_integer(self):
        '''
        Test get_n_predictions with n as a non-integer.
        '''
        # Creating a 1 predictions object
        preds = Predictions([self.pred1])

        # Check - Does it pick up a problem with non-integer predictions?
        with self.assertRaisesRegex(ValueError, 'The number of predictions \'n\' must be a positive integer.'):
            preds.get_n_predictions(1.5)

        # Does - Does it pick up a problem with a string instead of an integer?
        with self.assertRaisesRegex(ValueError, 'The number of predictions \'n\' must be a positive integer.'):
            preds.get_n_predictions('abc')

    def test_len_empty(self):
        '''
        Test __len__ for an empty collection.
        '''
        # Check - Does it identify a 0 length object?
        preds = Predictions()
        self.assertEqual(len(preds), 0)

    def test_len_with_items(self):
        '''
        Test __len__ for a collection with items.
        '''
        # Check - Creating a 2 length predictions object
        preds = Predictions(initial_predictions=[self.pred1, self.pred2])
        self.assertEqual(len(preds), 2)

        # Check - Add a prediction and check
        preds.add_prediction(self.pred3)
        self.assertEqual(len(preds), 3)

    # --- __getitem__ Tests ---
    def test_getitem_valid_index(self):
        '''
        Test __getitem__ with a valid index.
        '''
        # Setting up our predictions
        preds = Predictions(initial_predictions=[self.pred1, self.pred2])

        # Check - Are the objects in the correct place?
        self.assertEqual(preds[0], self.pred1)
        self.assertEqual(preds[1], self.pred2)

    def test_getitem_invalid_index_out_of_bounds(self):
        '''
        Test __getitem__ with an index out of bounds.
        '''
        # Creating a 1 length predictions object
        preds = Predictions(initial_predictions=[self.pred1])

        # Check - Identifies out of index (positive and negative)
        with self.assertRaises(IndexError):
            preds[1]
        with self.assertRaises(IndexError):
            preds[-2] 

    def test_getitem_invalid_index_type(self):
        '''
        Test __getitem__ with a non-integer index.
        '''
        # Creating a zero length
        preds = Predictions(initial_predictions=[self.pred1])

        # Check - trying other indices (string and floating point)
        with self.assertRaises(TypeError):
            preds['zero']
        with self.assertRaises(TypeError):
            preds[0.5]


if __name__ == '__main__':
    unittest.main(argv = ['first-arg-is-ignored'], exit = False)