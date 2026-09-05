import aiounittest
from unittest.mock import patch, MagicMock, AsyncMock
import io
import sys
import json
import httpx

from app.models.ollama_generative import OllamaModel

class TestOllamaModel(aiounittest.AsyncTestCase):
    def setUp(self):

        self.patcher = patch('models.ollama_generative.httpx.AsyncClient')

        self.mock_async_client_class = self.patcher.start()

        self.mock_client_instance = self.mock_async_client_class.return_value
        self.mock_client_instance.post = AsyncMock()

        self.model = OllamaModel(
            name    = 'TestOllama',
            api_url = 'http://fake-ollama-url:11434'
        )
    def tearDown(self):
        self.patcher.stop()

    def test_initialization(self):

        self.mock_async_client_class.assert_called_once_with(
            base_url = 'http://fake-ollama-url:11434',
            timeout  = 60.0
        )
        self.assertEqual(self.model.name, 'TestOllama')

        with self.assertRaises(ValueError):
            OllamaModel(name='Test', api_url='')

    def test_preprocess(self):
        input_text = 'This is a test.'
        payload    = self.model.preprocess(input_text)

        self.assertIsInstance(payload, dict)

        self.assertEqual(payload['model'], 'llama3')

        self.assertEqual(len(payload['messages']), 2)
        self.assertEqual(payload['messages'][0]['role'], 'system')
        self.assertEqual(payload['messages'][1]['role'], 'user')
        self.assertIn(input_text, payload['messages'][1]['content'])

    async def test_get_prediction_from_api_success(self):

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200

        inner_json_str = '{"hate_speech_probability": 0.9, "explanation": "Success!"}'

        mock_response.json.return_value = {
            "choices": [{"message": {"content": inner_json_str}}]
        }

        self.mock_client_instance.post.return_value = mock_response

        payload = self.model.preprocess('some input')
        result = await self.model._get_prediction_from_api(payload)

        self.mock_client_instance.post.assert_awaited_once_with('/v1/chat/completions', json=payload)

        mock_response.raise_for_status.assert_called_once()

        self.assertEqual(result['hate_speech_probability'], 0.9)
        self.assertEqual(result['explanation'], 'Success!')

    async def test_get_prediction_from_api_failures(self):

        self.mock_client_instance.post.side_effect = httpx.RequestError("Connection failed")

        payload = self.model.preprocess('some input')
        result = await self.model._get_prediction_from_api(payload)
        self.assertEqual(result['explanation'], 'Error: Could not get a valid response from the Ollama service.')

        malformed_inner_json = '{"hate_speech_probability": 0.9...this is broken'
        api_response_data = {"choices": [{"message": {"content": malformed_inner_json}}]}
        mock_response = httpx.Response(200, json=api_response_data)

        self.mock_client_instance.post.side_effect = None
        self.mock_client_instance.post.return_value = mock_response

        result = await self.model._get_prediction_from_api(payload)
        self.assertEqual(result['explanation'], 'Error: Could not get a valid response from the Ollama service.')

    async def test_predict_and_predict_text_methods(self):
        with patch.object(self.model, '_get_prediction_from_api', new_callable=AsyncMock) as mock_get_pred:
            mock_get_pred.return_value = {
                'hate_speech_probability': 0.95,
                'explanation': 'This is the explanation.'
            }
            payload = 'any payload'
            probability = await self.model.predict(payload)
            explanation = await self.model.predict_text(payload)

            self.assertEqual(probability, 0.95)
            self.assertEqual(explanation, 'This is the explanation.')

            mock_get_pred.return_value = {'error': 'Something went wrong'}
            probability = await self.model.predict(payload)
            explanation = await self.model.predict_text(payload)

            self.assertEqual(probability, 0.0)
            self.assertEqual(explanation, 'No explanation available.')

    def test_save_and_load_noop(self):

        captured_output = io.StringIO()
        sys.stdout = captured_output

        self.model.save('fake/path.pkl')
        self.assertIn("'TestOllama' is a remote API model and cannot be saved", captured_output.getvalue())

        self.model.load('fake/path.pkl')
        self.assertIn("'TestOllama' is a remote API model; no loading is required", captured_output.getvalue())

        sys.stdout = sys.__stdout__

if __name__ == '__main__':
    aiounittest.main()