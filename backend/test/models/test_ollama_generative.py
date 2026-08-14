import aiounittest
from unittest.mock import patch, MagicMock, AsyncMock
import io
import sys
import json
import httpx

# Import the class we are testing
from app.models.ollama_generative import OllamaModel

# A test suite for the OllamaModel class.
class TestOllamaModel(aiounittest.AsyncTestCase):
    '''
    Unit tests for the OllamaModel class. Mocks the external httpx client
    to test the model's logic without making real network calls.
    '''
    # Set up a new model instance and mock the httpx client before each test.
    def setUp(self):

        # Create a patcher for the httpx.AsyncClient.
        self.patcher = patch('models.ollama_generative.httpx.AsyncClient')

        # Start the patcher and get the mock class.
        self.mock_async_client_class = self.patcher.start()

        # Get the mock instance that will be created by the OllamaModel.
        self.mock_client_instance = self.mock_async_client_class.return_value
        self.mock_client_instance.post = AsyncMock()
        
        # Instantiate the class we want to test.
        self.model = OllamaModel(
            name    = 'TestOllama',
            api_url = 'http://fake-ollama-url:11434'
        )
    # Stop the patcher after each test.
    def tearDown(self):
        self.patcher.stop()

    # Test if the model initializes correctly.
    def test_initialization(self):

        # Check that the httpx client was initialized with the correct base URL.
        self.mock_async_client_class.assert_called_once_with(
            base_url = 'http://fake-ollama-url:11434',
            timeout  = 60.0
        )
        # Check that the model's name is set correctly.
        self.assertEqual(self.model.name, 'TestOllama')

        # Check that a ValueError is raised if no API URL is provided.
        with self.assertRaises(ValueError):
            OllamaModel(name='Test', api_url='')

    # Test if the preprocess method formats the JSON payload correctly.
    def test_preprocess(self):
        input_text = 'This is a test.'
        payload    = self.model.preprocess(input_text)
        
        # Check that the output is a dictionary.
        self.assertIsInstance(payload, dict)

        # Check for the correct model name.
        self.assertEqual(payload['model'], 'llama3')

        # Check that the messages array has the correct structure and content.
        self.assertEqual(len(payload['messages']), 2)
        self.assertEqual(payload['messages'][0]['role'], 'system')
        self.assertEqual(payload['messages'][1]['role'], 'user')
        self.assertIn(input_text, payload['messages'][1]['content'])

    # Test the internal API call method with a successful response.
    async def test_get_prediction_from_api_success(self):

        # Instead of a real httpx.Response, create a MagicMock that acts like one.
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        
        # Define the model's inner JSON response
        inner_json_str = '{"hate_speech_probability": 0.9, "explanation": "Success!"}'
        
        # Configure the mock response's .json() method to return the outer payload
        mock_response.json.return_value = {
            "choices": [{"message": {"content": inner_json_str}}]
        }
        
        # Set the return_value that the AsyncMock will produce when awaited.
        self.mock_client_instance.post.return_value = mock_response
        
        # --- The rest of the test is the same ---
        payload = self.model.preprocess('some input')
        result = await self.model._get_prediction_from_api(payload)
        
        # Assert: Check that the API was called correctly.
        self.mock_client_instance.post.assert_awaited_once_with('/v1/chat/completions', json=payload)
        
        # Assert that our mock's raise_for_status method was called.
        mock_response.raise_for_status.assert_called_once()

        # Assert that the inner JSON was parsed correctly.
        self.assertEqual(result['hate_speech_probability'], 0.9)
        self.assertEqual(result['explanation'], 'Success!')

    # Test the internal API call method with various failure modes.
    async def test_get_prediction_from_api_failures(self):

        # Arrange: Simulate an HTTP error (e.g., 500 Internal Server Error).
        self.mock_client_instance.post.side_effect = httpx.RequestError("Connection failed")
        
        # Act & Assert: Check for the default error response.
        payload = self.model.preprocess('some input')
        result = await self.model._get_prediction_from_api(payload)
        self.assertEqual(result['explanation'], 'Error: Could not get a valid response from the Ollama service.')

        # Arrange: Simulate a successful response with malformed inner JSON.
        malformed_inner_json = '{"hate_speech_probability": 0.9...this is broken'
        api_response_data = {"choices": [{"message": {"content": malformed_inner_json}}]}
        mock_response = httpx.Response(200, json=api_response_data)

        # Reset the mock's side_effect and set a new return_value.
        self.mock_client_instance.post.side_effect = None
        self.mock_client_instance.post.return_value = mock_response

        # Act & Assert: Check for the default error response again.
        result = await self.model._get_prediction_from_api(payload)
        self.assertEqual(result['explanation'], 'Error: Could not get a valid response from the Ollama service.')

    # Test the public predict and predict_text async methods.
    async def test_predict_and_predict_text_methods(self):
        # Use patch.object to mock the internal method for this test.
        with patch.object(self.model, '_get_prediction_from_api', new_callable=AsyncMock) as mock_get_pred:
            # --- Test success case ---
            mock_get_pred.return_value = {
                'hate_speech_probability': 0.95,
                'explanation': 'This is the explanation.'
            }
            payload = 'any payload'
            probability = await self.model.predict(payload)
            explanation = await self.model.predict_text(payload)
            
            self.assertEqual(probability, 0.95)
            self.assertEqual(explanation, 'This is the explanation.')
            
            # --- Test failure/default case ---
            mock_get_pred.return_value = {'error': 'Something went wrong'}
            probability = await self.model.predict(payload)
            explanation = await self.model.predict_text(payload)
            
            self.assertEqual(probability, 0.0)
            self.assertEqual(explanation, 'No explanation available.')
            
    # Test that the save and load methods are no-ops.
    def test_save_and_load_noop(self):
        
        # Capture stdout to check the print statements.
        captured_output = io.StringIO()
        sys.stdout = captured_output

        self.model.save('fake/path.pkl')
        self.assertIn("'TestOllama' is a remote API model and cannot be saved", captured_output.getvalue())

        self.model.load('fake/path.pkl')
        self.assertIn("'TestOllama' is a remote API model; no loading is required", captured_output.getvalue())
        
        # Restore stdout.
        sys.stdout = sys.__stdout__

if __name__ == '__main__':
    aiounittest.main()