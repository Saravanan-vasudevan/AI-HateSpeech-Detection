import unittest
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from unittest.mock import AsyncMock

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


class TestHuggingFaceAPI(unittest.IsolatedAsyncioTestCase):

    def tearDown(self):
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        dependency_func = get_model_dependency('huggingface')

        with self.assertRaises(HTTPException) as ctx:
            dependency_func()

        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        mock_model = MagicMock()
        load_model('huggingface', mock_model)

        dependency_func = get_model_dependency('huggingface')
        retrieved_model = dependency_func()

        self.assertIs(retrieved_model, mock_model)

    async def test_predict_hf_generative_success(self):
        mock_model = MagicMock()

        mock_model.predict.return_value = 0.95
        mock_model.predict_text.return_value = 'Contextual Explanation: This text is offensive.'

        load_model('huggingface', mock_model)

        request = PredictionRequest(text = 'some hateful text')

        response = await predict_hf_generative(request=request, model=mock_model)

        self.assertTrue(response.is_hate_speech)
        self.assertEqual(response.hate_speech_probability, 0.95)
        self.assertEqual(response.explanation, 'This text is offensive.')
        self.assertEqual(response.input_text, 'some hateful text')

    async def test_predict_hf_generative_internal_error(self):
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception('Model prediction failed')
        load_model('huggingface', mock_model)

        request = PredictionRequest(text = 'some text')

        with self.assertRaises(HTTPException) as ctx:
            await predict_hf_generative(request = request, model = mock_model)

        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestSklearnAPI(unittest.IsolatedAsyncioTestCase):

    def tearDown(self):
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        dependency_func = get_model_dependency('sklearn')
        with self.assertRaises(HTTPException) as ctx:
            dependency_func()

        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        mock_model = MagicMock()
        load_model('sklearn', mock_model)
        retrieved_model = get_model_dependency('sklearn')()

        self.assertIs(retrieved_model, mock_model)

    async def test_predict_sklearn_success(self):
        mock_model                           = MagicMock()
        mock_model.predict.return_value      = 0.88
        mock_model.predict_text.return_value = 'The model predicts HATE SPEECH with a confidence of 88.00%.'
        load_model('sklearn', mock_model)

        request = PredictionRequest(text = 'some bad words')

        response = await predict_sklearn(request=request, model=mock_model)

        self.assertTrue(response.is_hate_speech)
        self.assertEqual(response.hate_speech_probability, 0.88)
        self.assertIn('HATE SPEECH', response.explanation)

    async def test_predict_sklearn_internal_error(self):
        mock_model                     = MagicMock()
        mock_model.predict.side_effect = ValueError('Prediction failed')
        load_model('sklearn', mock_model)

        request = PredictionRequest(text = 'some text')

        with self.assertRaises(HTTPException) as ctx:
            await predict_sklearn(request = request, model = mock_model)

        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Prediction failed', ctx.exception.detail)


class TestGeminiAPI(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        dependency_func = get_model_dependency('gemini')
        with self.assertRaises(HTTPException) as ctx:
            dependency_func()

        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        mock_model = MagicMock()
        load_model('gemini', mock_model)
        retrieved_model = get_model_dependency('gemini')()

        self.assertIs(retrieved_model, mock_model)

    async def test_predict_gemini_success(self):
        mock_model = MagicMock()

        mock_model.preprocess.return_value = "preprocessed prompt"
        mock_model.predict.return_value = 0.99
        mock_model.predict_text.return_value = "This is definitely hate speech."
        load_model('gemini', mock_model)

        request  = PredictionRequest(text='some very bad words')
        response = await predict_gemini(request=request, model=mock_model)

        self.assertTrue(response.is_hate_speech)
        self.assertEqual(response.hate_speech_probability, 0.99)
        self.assertEqual(response.explanation, "This is definitely hate speech.")

        mock_model.preprocess.assert_called_once_with('some very bad words')
        mock_model.predict.assert_called_once_with("preprocessed prompt")

    async def test_predict_gemini_internal_error(self):
        mock_model = MagicMock()
        mock_model.preprocess.side_effect = Exception('Preprocessing failed')
        load_model('gemini', mock_model)

        request = PredictionRequest(text='some text')

        with self.assertRaises(HTTPException) as ctx:
            await predict_gemini(request=request, model=mock_model)
        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Preprocessing failed', ctx.exception.detail)


class TestOllamaAPI(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        dependency_func = get_model_dependency('ollama')

        with self.assertRaises(HTTPException) as ctx:
            dependency_func()

        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        mock_model = MagicMock()
        load_model('ollama', mock_model)

        retrieved_model = get_model_dependency('ollama')()

        self.assertIs(retrieved_model, mock_model)

    async def test_predict_ollama_success(self):
        mock_model = MagicMock()

        mock_model.preprocess.return_value = {'model': 'llama3', 'messages': []}
        mock_model.predict = AsyncMock(return_value=0.98)
        mock_model.predict_text = AsyncMock(return_value='This is the Ollama explanation.')
        load_model('ollama', mock_model)

        request = PredictionRequest(text='some text for ollama')
        response = await predict_ollama(request=request, model=mock_model)

        self.assertTrue(response.is_hate_speech)
        self.assertEqual(response.hate_speech_probability, 0.98)
        self.assertEqual(response.explanation, "This is the Ollama explanation.")

        mock_model.preprocess.assert_called_once_with('some text for ollama')
        mock_model.predict.assert_awaited_once_with({'model': 'llama3', 'messages': []})

    async def test_predict_ollama_internal_error(self):
        mock_model = MagicMock()

        mock_model.predict = AsyncMock(side_effect=Exception('Ollama prediction failed'))
        load_model('ollama', mock_model)

        request = PredictionRequest(text = 'some text')

        with self.assertRaises(HTTPException) as ctx:
            await predict_ollama(request = request, model = mock_model)

        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Ollama prediction failed', ctx.exception.detail)


class TestFeedbackAPI(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        _loaded_models.clear()

    def test_get_model_not_loaded(self):
        dependency_func = get_model_dependency('feedback')

        with self.assertRaises(HTTPException) as ctx:
            dependency_func()

        self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_load_and_get_model(self):
        mock_model = MagicMock()
        load_model('feedback', mock_model)

        retrieved_model = get_model_dependency('feedback')()

        self.assertIs(retrieved_model, mock_model)

    async def test_generate_feedback_success(self):
        mock_model = MagicMock()
        mock_model.generate.return_value = 'This is excellent and helpful feedback.'
        load_model('feedback', mock_model)

        request = FeedbackRequest(
            student_prediction=True,
            student_explanation='The student gave a correct reason.',
            ai_prediction=True,
            ai_explanation='The AI confirmed the reason.'
        )

        response = await generate_feedback(request=request, model=mock_model)

        self.assertEqual(response.feedback_text, 'This is excellent and helpful feedback.')

        mock_model.generate.assert_called_once_with(
            student_prediction=True,
            student_explanation='The student gave a correct reason.',
            ai_prediction=True,
            ai_explanation='The AI confirmed the reason.'
        )

    async def test_generate_feedback_internal_error(self):
        mock_model = MagicMock()
        mock_model.generate.side_effect = Exception('LLM generation failed')
        load_model('feedback', mock_model)

        request = FeedbackRequest(
            student_prediction=False,
            student_explanation='any reason',
            ai_prediction=True,
            ai_explanation='any reason'
        )

        with self.assertRaises(HTTPException) as ctx:
            await generate_feedback(request=request, model=mock_model)

        self.assertEqual(ctx.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        self.assertIn('LLM generation failed', ctx.exception.detail)

if __name__ == '__main__':
    unittest.main()