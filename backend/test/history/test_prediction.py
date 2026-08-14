import unittest
import datetime
from app.history.prediction import Prediction 

class TestPrediction(unittest.TestCase):
    '''
    Test cases for the Prediction class to ensure its robustness
    and correct behavior under various inputs, including valid
    data and invalid data that should raise specific errors.
    '''
    def setUp(self):
        '''
        Set up a dictionary of valid, default arguments to use in tests.
        This reduces code repetition in each test case.
        '''
        self.valid_args = {
            'username'          : 'test_user',
            'datetime_str'      : '2025-07-17T14:00:00Z',
            'text'              : 'This is a test comment.',
            'human'             : True,
            'ai'                : False,
            'human_explanation' : 'A valid human explanation.',
            'ai_explanation'    : 'A valid AI explanation.',
            'p'                 : 0.75
        }

    def test_successful_initialization(self):
        '''
        Verifies that a Prediction object can be successfully created
        when provided with all valid and correctly formatted inputs.
        It checks if the object is instantiated and if its internal
        attributes are set correctly.
        '''
        # Passing the arguments from the start-up
        prediction = Prediction(**self.valid_args)

        # Check that the object is created correctly
        self.assertIsInstance(prediction, Prediction)
        self.assertEqual(prediction._username, self.valid_args['username'])
        self.assertEqual(prediction._text, self.valid_args['text'])
        self.assertEqual(prediction._p, self.valid_args['p'])
        self.assertEqual(prediction._score, 0)  # Score is false due to disagreemnt

    def test_get_method_output(self):
        '''
        Tests that the `get()` method correctly retrieves and returns
        the prediction's attributes as a dictionary. It verifies both
        the structure and the values of the returned dictionary.
        '''
        # Passing the set-up dictionary against
        prediction = Prediction(**self.valid_args)
        
        # The expected output dictionary now includes all new fields
        # N.B - This is to ensure equality of values and not just pointer
        #       of the dictionary
        expected_output = {
            'username'         : 'test_user',
            'datetime'         : '2025-07-17T14:00:00+00:00',
            'text'             : 'This is a test comment.',
            'human_prediction' : True,
            'ai_prediction'    : False,
            'score'            : 0,
            'human_explanation': 'A valid human explanation.',
            'ai_explanation'   : 'A valid AI explanation.',
            'probability'      : 0.75
        }
        self.assertEqual(prediction.get(), expected_output)

    def test_invalid_parameter_types(self):
        '''
        Tests that a TypeError is raised for various invalid data types.
        '''
        # Test non-string username
        with self.assertRaisesRegex(ValueError, 'Username must be a non-empty string.'):
            Prediction(**{**self.valid_args, 'username': 123})
        
        # Test non-string text
        with self.assertRaisesRegex(ValueError, 'Text must be a non-empty string.'):
            Prediction(**{**self.valid_args, 'text': 123})

        # Test non-boolean human prediction
        with self.assertRaisesRegex(TypeError, 'Human prediction must be a boolean.'):
            Prediction(**{**self.valid_args, 'human': 'True'})
        
        # Test non-boolean AI prediction
        with self.assertRaisesRegex(TypeError, 'AI prediction must be a boolean.'):
            Prediction(**{**self.valid_args, 'ai': 0})
    
    def test_invalid_parameter_values(self):
        '''
        Tests that a ValueError is raised for various invalid values.
        '''
        # Test empty string username
        with self.assertRaisesRegex(ValueError, 'Username must be a non-empty string.'):
            Prediction(**{**self.valid_args, 'username': '   '})

        # Test empty string text
        with self.assertRaisesRegex(ValueError, 'Text must be a non-empty string.'):
            Prediction(**{**self.valid_args, 'text': ''})
            
        # Test invalid datetime string
        with self.assertRaisesRegex(ValueError, 'Datetime must be a valid, recognizable date/time string.'):
            Prediction(**{**self.valid_args, 'datetime_str': 'not-a-date'})

    def test_init_raises_error_for_invalid_explanations(self):
        '''
        Ensures a TypeError is raised if explanations are not strings.
        '''
        with self.assertRaisesRegex(TypeError, 'Human explanation must be a string.'):
            Prediction(**{**self.valid_args, 'human_explanation': 123})
            
        with self.assertRaisesRegex(TypeError, 'AI explanation must be a string.'):
            Prediction(**{**self.valid_args, 'ai_explanation': False})

    def test_init_raises_error_for_invalid_probability(self):
        '''
        Ensures errors are raised for invalid probability types and values.
        '''
        # Test for non-float probability
        with self.assertRaisesRegex(TypeError, 'Probability must be a float.'):
            Prediction(**{**self.valid_args, 'p': '0.5'})

        # Test for out-of-range probability (less than 0)
        with self.assertRaisesRegex(ValueError, 'Probability must be between 0.0 and 1.0.'):
            Prediction(**{**self.valid_args, 'p': -0.1})

        # Test for out-of-range probability (greater than 1)
        with self.assertRaisesRegex(ValueError, 'Probability must be between 0.0 and 1.0.'):
            Prediction(**{**self.valid_args, 'p': 1.1})

# This block allows you to run tests directly from the script
if __name__ == '__main__':
    unittest.main(argv = ['first-arg-is-ignored'], exit = False)