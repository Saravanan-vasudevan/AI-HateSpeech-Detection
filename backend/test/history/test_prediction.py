import unittest
import datetime
from app.history.prediction import Prediction

class TestPrediction(unittest.TestCase):
    def setUp(self):
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
        prediction = Prediction(**self.valid_args)

        self.assertIsInstance(prediction, Prediction)
        self.assertEqual(prediction._username, self.valid_args['username'])
        self.assertEqual(prediction._text, self.valid_args['text'])
        self.assertEqual(prediction._p, self.valid_args['p'])
        self.assertEqual(prediction._score, 0)

    def test_get_method_output(self):
        prediction = Prediction(**self.valid_args)

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
        with self.assertRaisesRegex(ValueError, 'Username must be a non-empty string.'):
            Prediction(**{**self.valid_args, 'username': 123})

        with self.assertRaisesRegex(ValueError, 'Text must be a non-empty string.'):
            Prediction(**{**self.valid_args, 'text': 123})

        with self.assertRaisesRegex(TypeError, 'Human prediction must be a boolean.'):
            Prediction(**{**self.valid_args, 'human': 'True'})

        with self.assertRaisesRegex(TypeError, 'AI prediction must be a boolean.'):
            Prediction(**{**self.valid_args, 'ai': 0})

    def test_invalid_parameter_values(self):
        with self.assertRaisesRegex(ValueError, 'Username must be a non-empty string.'):
            Prediction(**{**self.valid_args, 'username': '   '})

        with self.assertRaisesRegex(ValueError, 'Text must be a non-empty string.'):
            Prediction(**{**self.valid_args, 'text': ''})

        with self.assertRaisesRegex(ValueError, 'Datetime must be a valid, recognizable date/time string.'):
            Prediction(**{**self.valid_args, 'datetime_str': 'not-a-date'})

    def test_init_raises_error_for_invalid_explanations(self):
        with self.assertRaisesRegex(TypeError, 'Human explanation must be a string.'):
            Prediction(**{**self.valid_args, 'human_explanation': 123})

        with self.assertRaisesRegex(TypeError, 'AI explanation must be a string.'):
            Prediction(**{**self.valid_args, 'ai_explanation': False})

    def test_init_raises_error_for_invalid_probability(self):
        with self.assertRaisesRegex(TypeError, 'Probability must be a float.'):
            Prediction(**{**self.valid_args, 'p': '0.5'})

        with self.assertRaisesRegex(ValueError, 'Probability must be between 0.0 and 1.0.'):
            Prediction(**{**self.valid_args, 'p': -0.1})

        with self.assertRaisesRegex(ValueError, 'Probability must be between 0.0 and 1.0.'):
            Prediction(**{**self.valid_args, 'p': 1.1})

if __name__ == '__main__':
    unittest.main(argv = ['first-arg-is-ignored'], exit = False)
