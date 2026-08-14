import unittest
from unittest.mock import patch, Mock
import io
import sys

# Importing the base model and model under test
from app.models.base_model import BaseModel
from app.models.gemini_generative import GeminiHateSpeechModel

class TestGeminiHateSpeechModel(unittest.TestCase):

    def setUp(self):
        '''
        Set up a new model instance before each test.
        Manually start patchers here to ensure mocks are active for initialization.
        '''
        # Start patchers manually
        self.patcher_generative_model = patch('models.gemini_generative.genai.GenerativeModel')
        self.patcher_configure = patch('models.gemini_generative.genai.configure')

        # Get the mock objects
        self.mock_generative_model_class = self.patcher_generative_model.start()
        self.mock_configure = self.patcher_configure.start()
        
        # Mock instance when calling GeminiModel
        self.mock_model_instance = self.mock_generative_model_class.return_value
        
        # Instantiate the class we want to test
        self.model = GeminiHateSpeechModel(
            name   = 'TestGemini',
            api_key='FAKE_API_KEY'
        )
        # Referencing the mock instance
        self.mock_api_call = self.mock_model_instance.generate_content

    def tearDown(self):
        '''
        Stop all patchers after each test to avoid side-effects.
        '''
        # Stopping the patchers
        self.patcher_generative_model.stop()
        self.patcher_configure.stop()

    def test_initialization(self):
        '''
        Test if the model initializes correctly.
        '''
        # Check - Was fake API call used once?
        self.mock_configure.assert_called_once_with(api_key = 'FAKE_API_KEY')

        # Check - Was the model called once with the right name?
        self.mock_generative_model_class.assert_called_once_with('gemini-1.5-flash')
        
        # Check - Is the internal model name saved?
        self.assertEqual(self.model.name, 'TestGemini')
        
        # Check - Are the internal history none initially?
        self.assertIsNone(self.model._last_input)
        self.assertIsNone(self.model._last_response)

    def test_preprocess(self):
        '''
        Test if the preprocess method formats the prompt correctly.
        '''
        # Components of prompt (both new inputs and presets)
        input_text     = 'This is a test text.'
        expected_start = 'You are a content moderation expert.'
        
        # Corrected indentation to 8 spaces to match the source file
        expected_end_block = f'        ---\n        {input_text}\n        ---'
        
        # Processing the inouts
        processed_text = self.model.preprocess(input_text)
        
        # Check - Is prompt correct?
        self.assertTrue(processed_text.startswith(expected_start))
        self.assertIn(expected_end_block, processed_text)

    def test_get_prediction_from_api_success(self):
        '''
        Test the internal API call method with a successful, valid JSON response.
        '''
        # Creating a mock response
        mock_response = Mock()
        mock_response.text = '```json\n{"hate_speech_probability": 0.9, "explanation": "This is hate speech."}\n```'
        self.mock_api_call.return_value = mock_response

        # Processing some input
        prompt = self.model.preprocess('some input')
        result = self.model._get_prediction_from_api(prompt)

        # Check - Was preprocess only called once?
        self.mock_api_call.assert_called_once_with(prompt)
        
        # Check - Were the probability and explanation expected?
        self.assertEqual(result['hate_speech_probability'], 0.9)
        self.assertEqual(result['explanation'], 'This is hate speech.')

    def test_get_prediction_from_api_json_error(self):
        '''
        Test the internal API call method when the API returns malformed JSON.
        '''
        # creating an erroneous mock response
        mock_response                   = Mock()
        mock_response.text              = 'This is not JSON.'
        self.mock_api_call.return_value = mock_response

        # Pre-processing and getting results
        prompt = self.model.preprocess('some input')
        result = self.model._get_prediction_from_api(prompt)

        # Check - Is the prompt and results as expected?
        self.assertEqual(result['hate_speech_probability'], 0.0)
        self.assertEqual(result['explanation'], 'Error: Could not parse model output.')

    def test_caching_logic(self):
        '''
        Test that the model caches responses and avoids redundant API calls.
        '''
        # Creating and specifying behaviour mock
        mock_response = Mock()
        mock_response.text = '{"hate_speech_probability": 0.8, "explanation": "Cached."}'
        self.mock_api_call.return_value = mock_response
        
        # Pre-processing the answer
        prompt = self.model.preprocess('some input')

        # First call
        result1 = self.model._get_prediction_from_api(prompt)
        self.mock_api_call.assert_called_once()

        # Second call with same input
        result2 = self.model._get_prediction_from_api(prompt)
        self.mock_api_call.assert_called_once() 
        self.assertEqual(result2, result1)

        # Third call with different input
        new_prompt = self.model.preprocess('different input')
        result3 = self.model._get_prediction_from_api(new_prompt)
        self.assertEqual(self.mock_api_call.call_count, 2)
        
    def test_predict_and_predict_text_methods(self):
        '''
        Test the public predict and predict_text methods.
        '''
        # Use patch.object to mock the internal method for this specific test
        with patch.object(self.model, '_get_prediction_from_api') as mock_get_pred:
            
            # Test success case
            mock_get_pred.return_value = {
                'hate_speech_probability': 0.95,
                'explanation': 'This is the explanation.'
            }
            # Speifying a prompt and answer
            prompt = 'any prompt'
            probability = self.model.predict(prompt)
            explanation = self.model.predict_text(prompt)
            
            # Check - Were results expected?
            self.assertEqual(probability, 0.95)
            self.assertEqual(explanation, 'This is the explanation.')
            
            # Test error/default case
            mock_get_pred.return_value = {'error': 'Something went wrong'}
            
            # Creating the error response
            probability = self.model.predict(prompt)
            explanation = self.model.predict_text(prompt)

            # Check - Were errors response expected?
            self.assertEqual(probability, 0.0)
            self.assertEqual(explanation, 'No explanation available.')

    def test_save_and_load_noop(self):
        '''
        Test that the save and load methods are no-ops and print messages.
        '''
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Dummy save function
        self.model.save('fake/path.pkl')
        self.assertIn("'TestGemini' is a cloud-based API model and cannot be saved", captured_output.getvalue())

        # Dummy load function
        self.model.load('fake/path.pkl')
        self.assertIn("'TestGemini' is a cloud-based API model; no loading", captured_output.getvalue())
        
        sys.stdout = sys.__stdout__

if __name__ == '__main__':
    unittest.main()