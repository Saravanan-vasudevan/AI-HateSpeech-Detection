import unittest
from unittest.mock import patch, Mock
import io
import sys

from app.models.base_model import BaseModel
from app.models.gemini_generative import GeminiHateSpeechModel

class TestGeminiHateSpeechModel(unittest.TestCase):

    def setUp(self):
        self.patcher_generative_model = patch('models.gemini_generative.genai.GenerativeModel')
        self.patcher_configure = patch('models.gemini_generative.genai.configure')

        self.mock_generative_model_class = self.patcher_generative_model.start()
        self.mock_configure = self.patcher_configure.start()

        self.mock_model_instance = self.mock_generative_model_class.return_value

        self.model = GeminiHateSpeechModel(
            name   = 'TestGemini',
            api_key='FAKE_API_KEY'
        )
        self.mock_api_call = self.mock_model_instance.generate_content

    def tearDown(self):
        self.patcher_generative_model.stop()
        self.patcher_configure.stop()

    def test_initialization(self):
        self.mock_configure.assert_called_once_with(api_key = 'FAKE_API_KEY')

        self.mock_generative_model_class.assert_called_once_with('gemini-1.5-flash')

        self.assertEqual(self.model.name, 'TestGemini')

        self.assertIsNone(self.model._last_input)
        self.assertIsNone(self.model._last_response)

    def test_preprocess(self):
        input_text     = 'This is a test text.'
        expected_start = 'You are a content moderation expert.'

        expected_end_block = f'        ---\n        {input_text}\n        ---'

        processed_text = self.model.preprocess(input_text)

        self.assertTrue(processed_text.startswith(expected_start))
        self.assertIn(expected_end_block, processed_text)

    def test_get_prediction_from_api_success(self):
        mock_response = Mock()
        mock_response.text = '```json\n{"hate_speech_probability": 0.9, "explanation": "This is hate speech."}\n```'
        self.mock_api_call.return_value = mock_response

        prompt = self.model.preprocess('some input')
        result = self.model._get_prediction_from_api(prompt)

        self.mock_api_call.assert_called_once_with(prompt)

        self.assertEqual(result['hate_speech_probability'], 0.9)
        self.assertEqual(result['explanation'], 'This is hate speech.')

    def test_get_prediction_from_api_json_error(self):
        mock_response                   = Mock()
        mock_response.text              = 'This is not JSON.'
        self.mock_api_call.return_value = mock_response

        prompt = self.model.preprocess('some input')
        result = self.model._get_prediction_from_api(prompt)

        self.assertEqual(result['hate_speech_probability'], 0.0)
        self.assertEqual(result['explanation'], 'Error: Could not parse model output.')

    def test_caching_logic(self):
        mock_response = Mock()
        mock_response.text = '{"hate_speech_probability": 0.8, "explanation": "Cached."}'
        self.mock_api_call.return_value = mock_response

        prompt = self.model.preprocess('some input')

        result1 = self.model._get_prediction_from_api(prompt)
        self.mock_api_call.assert_called_once()

        result2 = self.model._get_prediction_from_api(prompt)
        self.mock_api_call.assert_called_once()
        self.assertEqual(result2, result1)

        new_prompt = self.model.preprocess('different input')
        result3 = self.model._get_prediction_from_api(new_prompt)
        self.assertEqual(self.mock_api_call.call_count, 2)

    def test_predict_and_predict_text_methods(self):
        with patch.object(self.model, '_get_prediction_from_api') as mock_get_pred:

            mock_get_pred.return_value = {
                'hate_speech_probability': 0.95,
                'explanation': 'This is the explanation.'
            }
            prompt = 'any prompt'
            probability = self.model.predict(prompt)
            explanation = self.model.predict_text(prompt)

            self.assertEqual(probability, 0.95)
            self.assertEqual(explanation, 'This is the explanation.')

            mock_get_pred.return_value = {'error': 'Something went wrong'}

            probability = self.model.predict(prompt)
            explanation = self.model.predict_text(prompt)

            self.assertEqual(probability, 0.0)
            self.assertEqual(explanation, 'No explanation available.')

    def test_save_and_load_noop(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output

        self.model.save('fake/path.pkl')
        self.assertIn("'TestGemini' is a cloud-based API model and cannot be saved", captured_output.getvalue())

        self.model.load('fake/path.pkl')
        self.assertIn("'TestGemini' is a cloud-based API model; no loading", captured_output.getvalue())

        sys.stdout = sys.__stdout__

if __name__ == '__main__':
    unittest.main()