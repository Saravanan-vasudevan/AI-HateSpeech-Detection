import unittest
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from unittest.mock import AsyncMock

# Imports
from app.models.api import (
    load_model,
    get_model_dependency,
    PredictionRequest,
    predict_hf_generative,
    predict_sklearn,
    predict_gemini,
    predict_ollama,
    _loaded_models,
    FeedbackRequest,
    FeedbackResponse,
    generate_feedback
)

############################################################
#        Tests for Model 1 - HuggingFaceGenerative         #
############################################################

class TestHuggingFaceAPI(unittest.IsolatedAsyncioTestCase):
    '''
    Test suite for the HuggingFaceGenerative model API endpoints.
    '''

    def tearDown(self):
        '''
        Ensures the model registry is cleared after each test.
        '''
        # Clearing the list of models
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        '''
        Tests that the dependency raises a 503 if the model isn't loaded.
        '''
        # Get the dependency function for the 'huggingface' model
        dependency_func = get_model_dependency('huggingface')

        # Check - did we get an exception without modelling?
        with self.assertRaises(HTTPException) as ctx:
            dependency_func() # Call it directly to test the "not found" logic
        
        # Check - Is the code correct?
        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        '''
        Tests that a model can be loaded and then retrieved successfully.
        '''
        # Create a mock hugging face model
        mock_model = MagicMock()
        load_model('huggingface', mock_model)
        
        # Retrieving the model
        dependency_func = get_model_dependency('huggingface')
        retrieved_model = dependency_func()
        
        # Check the model is of the right type?
        self.assertIs(retrieved_model, mock_model)

    async def test_predict_hf_generative_success(self):
        '''
        Tests a successful prediction from the HuggingFace endpoint.
        '''
        # Creating the mock model
        mock_model = MagicMock()

        # Specifying the return value of the model
        mock_model.predict.return_value = 0.95
        mock_model.predict_text.return_value = 'Contextual Explanation: This text is offensive.'
        
        # Loading the model
        load_model('huggingface', mock_model)
        
        # Use the generic request object
        request = PredictionRequest(text = 'some hateful text')
        
        # Call the endpoint directly, passing the mock model
        response = await predict_hf_generative(request=request, model=mock_model)

        # Check are all the attributes correct?
        self.assertTrue(response.is_hate_speech)
        self.assertEqual(response.hate_speech_probability, 0.95)
        self.assertEqual(response.explanation, 'This text is offensive.')
        self.assertEqual(response.input_text, 'some hateful text')

    async def test_predict_hf_generative_internal_error(self):
        '''
        Tests that a 500 error is raised if the model fails.
        '''
        # Creating a model and specifying the errors?
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception('Model prediction failed')
        load_model('huggingface', mock_model)
        
        # Passing the request to the model
        request = PredictionRequest(text = 'some text')
        
        # Check - Was an error raised?
        with self.assertRaises(HTTPException) as ctx:
            await predict_hf_generative(request = request, model = mock_model)
        
        # Check - Was the exception correct?
        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             Tests for Model 2 - SklearnModel             #
############################################################

class TestSklearnAPI(unittest.IsolatedAsyncioTestCase):
    '''
    Test suite for the SklearnModel API endpoints.
    '''

    def tearDown(self):
        '''
        Closing down the test suite
        '''
        # Clearing the list of models
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        '''
        Tests that the dependency raises a 503 if the model isn't loaded.
        '''
        # Retrieving the model
        dependency_func = get_model_dependency('sklearn')
        with self.assertRaises(HTTPException) as ctx:
            dependency_func()
        
        # Check - Is the exception code correct?
        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        '''
        Tests that a model can be loaded and retrieved.
        '''
        # Creating the model
        mock_model = MagicMock()
        load_model('sklearn', mock_model)
        retrieved_model = get_model_dependency('sklearn')()
        
        # Check - Is the model of the correct type?
        self.assertIs(retrieved_model, mock_model)

    async def test_predict_sklearn_success(self):
        '''
        Tests a successful prediction from the Sklearn endpoint.
        '''
        # Specifying the returns of the model
        mock_model                           = MagicMock()
        mock_model.predict.return_value      = 0.88
        mock_model.predict_text.return_value = 'The model predicts HATE SPEECH with a confidence of 88.00%.'
        load_model('sklearn', mock_model)

        # Creating th request
        request = PredictionRequest(text = 'some bad words')
        
        # Passing the request to the model
        response = await predict_sklearn(request=request, model=mock_model)
        
        # Check - Were all the responses correct?
        self.assertTrue(response.is_hate_speech)
        self.assertEqual(response.hate_speech_probability, 0.88)
        self.assertIn('HATE SPEECH', response.explanation)

    async def test_predict_sklearn_internal_error(self):
        '''
        Tests that a 500 error is raised if the model fails.
        '''
        # Specifying a model with exceptions
        mock_model                     = MagicMock()
        mock_model.predict.side_effect = ValueError('Prediction failed')
        load_model('sklearn', mock_model)
        
        # Creating the request
        request = PredictionRequest(text = 'some text')

        # Handling the exception
        with self.assertRaises(HTTPException) as ctx:
            await predict_sklearn(request = request, model = mock_model)
        
        # Check - Was the exception incorrrect?
        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Prediction failed', ctx.exception.detail)

############################################################
#         Tests for Model 3 - GeminiHateSpeechModel        #
############################################################

class TestGeminiAPI(unittest.IsolatedAsyncioTestCase):
    '''
    Test suite for the GeminiHateSpeechModel API endpoints.
    '''
    def tearDown(self):
        '''
        Closes down the testing suite at the
        end of the testing
        '''
        # Clearing the output
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        '''
        Tests that the dependency raises a 503 if the model isn't loaded.
        '''
        dependency_func = get_model_dependency('gemini')
        with self.assertRaises(HTTPException) as ctx:
            dependency_func()
        
        # Check - Was a 503 exception raised?
        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        '''
        Tests that a model can be loaded and retrieved.
        '''
        # Loading the model
        mock_model = MagicMock()
        load_model('gemini', mock_model)
        retrieved_model = get_model_dependency('gemini')()
        
        # Check - Is the model of the correct type?
        self.assertIs(retrieved_model, mock_model)

    async def test_predict_gemini_success(self):
        '''
        Tests a successful prediction from the Gemini endpoint.
        '''
        mock_model = MagicMock()

        # Mock all methods used by the endpoint
        mock_model.preprocess.return_value = "preprocessed prompt"
        mock_model.predict.return_value = 0.99
        mock_model.predict_text.return_value = "This is definitely hate speech."
        load_model('gemini', mock_model)

        # Passing a request and getting its response
        request  = PredictionRequest(text='some very bad words')
        response = await predict_gemini(request=request, model=mock_model)
        
        # Check - Were the corret parameters returned?
        self.assertTrue(response.is_hate_speech)
        self.assertEqual(response.hate_speech_probability, 0.99)
        self.assertEqual(response.explanation, "This is definitely hate speech.")
        
        # Check - Were all the methods only called once?
        mock_model.preprocess.assert_called_once_with('some very bad words')
        mock_model.predict.assert_called_once_with("preprocessed prompt")

    async def test_predict_gemini_internal_error(self):
        '''
        Tests that a 500 error is raised if the model fails.
        '''
        mock_model = MagicMock()
        mock_model.preprocess.side_effect = Exception('Preprocessing failed')
        load_model('gemini', mock_model)
        
        request = PredictionRequest(text='some text')

        with self.assertRaises(HTTPException) as ctx:
            await predict_gemini(request=request, model=mock_model)
        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Preprocessing failed', ctx.exception.detail)

############################################################
#        Tests for Model 4 - OllamaModel (Self-Hosted)     #
############################################################

class TestOllamaAPI(unittest.IsolatedAsyncioTestCase):
    '''
    Test suite for the self-hosted OllamaModel API endpoint.
    '''
    def tearDown(self):
        '''
        Ensures the model registry is cleared after each test.
        '''
        # Clearing the list of models
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        '''
        Tests that the dependency raises a 503 if the model isn't loaded.
        '''
        # Retrieving model without loading first
        dependency_func = get_model_dependency('ollama')

        # Check: Is HTTP exception raised?
        with self.assertRaises(HTTPException) as ctx:
            dependency_func()
        
        # Check: Is HTTP error a 503
        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        '''
        Tests that the Ollama model can be loaded and retrieved.
        '''
        # Mocking the model
        mock_model = MagicMock()
        load_model('ollama', mock_model)

        # Retrieving the model
        retrieved_model = get_model_dependency('ollama')()
        
        # Check: Is this model of the correct type?
        self.assertIs(retrieved_model, mock_model)

    async def test_predict_ollama_success(self):
        '''
        Tests a successful prediction from the Ollama endpoint.
        '''
        mock_model = MagicMock()

        # Mock all methods used by the endpoint.
        mock_model.preprocess.return_value = {'model': 'llama3', 'messages': []}
        mock_model.predict = AsyncMock(return_value=0.98)
        mock_model.predict_text = AsyncMock(return_value='This is the Ollama explanation.')
        load_model('ollama', mock_model)

        # Create the request and get the response by calling the endpoint function.
        request = PredictionRequest(text='some text for ollama')
        response = await predict_ollama(request=request, model=mock_model)
        
        # Check if the response is correct.
        self.assertTrue(response.is_hate_speech)
        self.assertEqual(response.hate_speech_probability, 0.98)
        self.assertEqual(response.explanation, "This is the Ollama explanation.")
        
        # Check that the mock methods were called/awaited correctly.
        mock_model.preprocess.assert_called_once_with('some text for ollama')
        mock_model.predict.assert_awaited_once_with({'model': 'llama3', 'messages': []})

    async def test_predict_ollama_internal_error(self):
        '''
        Tests that a 500 error is raised if the Ollama model fails.
        '''
        # Creating the model again
        mock_model = MagicMock()

        # Configure an async method to raise an error.
        mock_model.predict = AsyncMock(side_effect=Exception('Ollama prediction failed'))
        load_model('ollama', mock_model)
        
        # Passing a request to the mock
        request = PredictionRequest(text = 'some text')

        # Check: Predict HTTP exception
        with self.assertRaises(HTTPException) as ctx:
            await predict_ollama(request = request, model = mock_model)
            
        # Check: Is this error code 500
        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Ollama prediction failed', ctx.exception.detail)

############################################################
#         Tests for Service 1 - FeedbackGenerator          #
############################################################

class TestFeedbackAPI(unittest.IsolatedAsyncioTestCase):
    '''
    Test suite for the FeedbackGenerator API endpoint.
    '''
    def tearDown(self):
        '''
        Ensures the model registry is cleared after each test.
        '''
        # Clearing the list of models
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        '''
        Tests that the dependency raises a 503 if the 'feedback' model isn't loaded.
        '''
        # Get the dependency function for the 'feedback' model
        dependency_func = get_model_dependency('feedback')

        # Check that an exception is raised when the model is not found
        with self.assertRaises(HTTPException) as ctx:
            dependency_func()
        
        # Verify the status code is 503 Service Unavailable
        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        '''
        Tests that the feedback model can be loaded and then retrieved successfully.
        '''
        # Create a mock feedback generator model
        mock_model = MagicMock()
        load_model('feedback', mock_model)
        
        # Retrieve the model using the dependency
        retrieved_model = get_model_dependency('feedback')()
        
        # Check that the retrieved model is the same one we loaded
        self.assertIs(retrieved_model, mock_model)

    async def test_generate_feedback_success(self):
        '''
        Tests a successful feedback generation request.
        '''
        # Create a mock model and configure its 'generate' method
        mock_model = MagicMock()
        mock_model.generate.return_value = 'This is excellent and helpful feedback.'
        load_model('feedback', mock_model)
        
        # Create a request payload using the FeedbackRequest model
        request = FeedbackRequest(
            student_prediction=True,
            student_explanation='The student gave a correct reason.',
            ai_prediction=True,
            ai_explanation='The AI confirmed the reason.'
        )
        
        # Call the endpoint function directly with the request and mock model
        response = await generate_feedback(request=request, model=mock_model)

        # Assert that the response contains the correct feedback text
        self.assertEqual(response.feedback_text, 'This is excellent and helpful feedback.')
        
        # Assert that the model's generate method was called once with the correct arguments
        mock_model.generate.assert_called_once_with(
            student_prediction=True,
            student_explanation='The student gave a correct reason.',
            ai_prediction=True,
            ai_explanation='The AI confirmed the reason.'
        )

    async def test_generate_feedback_internal_error(self):
        '''
        Tests that a 500 error is raised if the feedback model fails internally.
        '''
        # Create a mock model and configure it to raise an exception
        mock_model = MagicMock()
        mock_model.generate.side_effect = Exception('LLM generation failed')
        load_model('feedback', mock_model)
        
        # Create the request payload
        request = FeedbackRequest(
            student_prediction=False,
            student_explanation='any reason',
            ai_prediction=True,
            ai_explanation='any reason'
        )
        
        # Check that calling the endpoint raises an HTTPException
        with self.assertRaises(HTTPException) as ctx:
            await generate_feedback(request=request, model=mock_model)
        
        # Verify the status code is 500 Internal Server Error
        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Verify the exception detail contains the original error message
        self.assertIn('LLM generation failed', ctx.exception.detail)

# This allows running the tests from the command line
if __name__ == '__main__':
    unittest.main()