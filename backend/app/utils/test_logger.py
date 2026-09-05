
import unittest

from bson import ObjectId

from app.utils.prediction_logger import PredictionLogger

class TestPredictionLogger(unittest.TestCase):
    '''
    Unit test suite for validating the functionality of PredictionLogger.

    This test class ensures that predictions are correctly logged into MongoDB,
    and the resulting entries match the input data.
    '''

    def setUp(self):
        '''
        Setup method that runs before each test.

        - Initializes a new instance of PredictionLogger
        - Defines a sample input, label, human feedback, and reason string
        '''
        self.logger = PredictionLogger()
        self.test_input = "This is a test input"
        self.test_ai_label = "not hate"
        self.test_human_label = "not hate"
        self.test_reason = "Test reason for unit testing"

    def test_log_prediction(self):
        '''
        Tests the log_prediction method.

        Verifies:
        - A document is successfully inserted (i.e., returns an ObjectId)
        - The inserted document matches the expected field values
        '''
        inserted_id = self.logger.log_prediction(
            input_text=self.test_input,
            label=self.test_ai_label,
            human_label=self.test_human_label,
            reason=self.test_reason,
            username="test_user"
        )

        self.assertIsNotNone(inserted_id)

        result = self.logger.collection.find_one({"_id": ObjectId(inserted_id)})

        self.assertIsNotNone(result)
        self.assertEqual(result["input_text"], self.test_input)
        self.assertEqual(result["AI_label"], self.test_ai_label)
        self.assertEqual(result["Human_label"], self.test_human_label)
        self.assertEqual(result["reason"], self.test_reason)

    def tearDown(self):
        '''
        Cleanup method that runs after each test.

        - Deletes any documents created during the test to maintain database hygiene
        - Closes the database connection
        '''
        self.logger.collection.delete_many({"input_text": self.test_input})
        self.logger.db.close_connection()

if __name__ == "__main__":
    unittest.main()
