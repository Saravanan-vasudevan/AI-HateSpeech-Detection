import unittest
import datetime
from dateutil.parser import parse as dateutil_parse
from app.history.prediction import Prediction
from app.history.predictions import Predictions

class TestPredictions(unittest.TestCase):

    def setUp(self):
        self.pred1 = Prediction('u1', '2024-01-01 10:00:00', 'text1', True, True)
        self.pred2 = Prediction('u2', '2024-01-05 11:00:00', 'text2', False, True)
        self.pred3 = Prediction('u3', '2024-01-03 12:00:00', 'text3', True, False)
        self.pred4 = Prediction('u4', '2024-01-07 13:00:00', 'text4', False, False)

    def test_predictions_initialization_empty(self):
        preds = Predictions()

        self.assertIsInstance(preds, Predictions)

        self.assertEqual(len(preds), 0)

    def test_predictions_initialization_with_list(self):
        initial_list = [self.pred1, self.pred2]

        preds = Predictions(initial_predictions=initial_list)

        self.assertEqual(len(preds), 2)

        self.assertIn(self.pred1, preds._predictions)

        self.assertIn(self.pred2, preds._predictions)

    def test_predictions_initialization_with_non_list(self):
        with self.assertRaisesRegex(TypeError, 'Initial_predictions must be a list of Prediction objects.'):
            Predictions(initial_predictions = 'not a list')

    def test_predictions_initialization_with_list_containing_non_prediction(self):
        initial_list = [self.pred1, 'not a prediction']
        with self.assertRaisesRegex(TypeError, "Only instances of 'Prediction' can be added."):
            Predictions(initial_predictions=initial_list)

    def test_add_prediction_valid(self):
        preds = Predictions()

        self.assertEqual(len(preds), 0)

        preds.add_prediction(self.pred1)
        self.assertEqual(len(preds), 1)

        self.assertIn(self.pred1, preds._predictions)

    def test_add_prediction_invalid_type(self):
        preds = Predictions()

        with self.assertRaisesRegex(TypeError, "Only instances of 'Prediction' can be added."):
            preds.add_prediction('not a prediction object')

    def test_get_n_predictions_all(self):
        preds = Predictions(initial_predictions=[self.pred1, self.pred2, self.pred3, self.pred4])

        result = preds.get_n_predictions(5)
        self.assertEqual(len(result), 4)

        self.assertEqual(result[0], self.pred4)
        self.assertEqual(result[1], self.pred2)
        self.assertEqual(result[2], self.pred3)
        self.assertEqual(result[3], self.pred1)

    def test_get_n_predictions_subset(self):
        preds = Predictions(initial_predictions=[self.pred1, self.pred2, self.pred3, self.pred4])

        result = preds.get_n_predictions(2)
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0], self.pred4)
        self.assertEqual(result[1], self.pred2)

    def test_get_n_predictions_empty_collection(self):
        preds = Predictions()
        result = preds.get_n_predictions(1)

        self.assertEqual(len(result), 0)

        self.assertEqual(result, [])

    def test_get_n_predictions_n_equals_zero(self):
        preds = Predictions([self.pred1])
        with self.assertRaisesRegex(ValueError, 'The number of predictions \'n\' must be a positive integer.'):
            preds.get_n_predictions(0)

    def test_get_n_predictions_n_negative(self):
        preds = Predictions([self.pred1])

        with self.assertRaisesRegex(ValueError, 'The number of predictions \'n\' must be a positive integer.'):
            preds.get_n_predictions(-1)

    def test_get_n_predictions_n_non_integer(self):
        preds = Predictions([self.pred1])

        with self.assertRaisesRegex(ValueError, 'The number of predictions \'n\' must be a positive integer.'):
            preds.get_n_predictions(1.5)

        with self.assertRaisesRegex(ValueError, 'The number of predictions \'n\' must be a positive integer.'):
            preds.get_n_predictions('abc')

    def test_len_empty(self):
        preds = Predictions()
        self.assertEqual(len(preds), 0)

    def test_len_with_items(self):
        preds = Predictions(initial_predictions=[self.pred1, self.pred2])
        self.assertEqual(len(preds), 2)

        preds.add_prediction(self.pred3)
        self.assertEqual(len(preds), 3)

    def test_getitem_valid_index(self):
        preds = Predictions(initial_predictions=[self.pred1, self.pred2])

        self.assertEqual(preds[0], self.pred1)
        self.assertEqual(preds[1], self.pred2)

    def test_getitem_invalid_index_out_of_bounds(self):
        preds = Predictions(initial_predictions=[self.pred1])

        with self.assertRaises(IndexError):
            preds[1]
        with self.assertRaises(IndexError):
            preds[-2]

    def test_getitem_invalid_index_type(self):
        preds = Predictions(initial_predictions=[self.pred1])

        with self.assertRaises(TypeError):
            preds['zero']
        with self.assertRaises(TypeError):
            preds[0.5]


if __name__ == '__main__':
    unittest.main(argv = ['first-arg-is-ignored'], exit = False)