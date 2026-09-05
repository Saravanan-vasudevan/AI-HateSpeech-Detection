from app.models.base_model import BaseModel
import httpx
import json


class OllamaModel(BaseModel):
    """Talks to a self-hosted Ollama instance (or Cloud Run endpoint) using
    the OpenAI-compatible /v1/chat/completions route.

    Same caching trick as the Gemini wrapper -- avoids double API calls when
    predict() and predict_text() are called with the same payload.
    """

    def __init__(self, name: str, model_name: str = 'llama3', api_url: str = ''):
        super().__init__(name)
        if not api_url:
            raise ValueError('OLLAMA_API_URL is required.')
        self._model_name = model_name
        self._api_url    = api_url
        self.client      = httpx.AsyncClient(base_url=api_url, timeout=300.0)
        self._last_input    = None
        self._last_response = None

    def preprocess(self, text: str) -> dict:
        """Build the chat-completions payload with a system prompt that asks
        for JSON output."""
        system_prompt = (
            'You are a content moderation expert. Analyze the following text for hate speech. '
            'Respond ONLY with a valid JSON object. The JSON object must contain two keys: '
            '1. "hate_speech_probability": A float between 0.0 and 1.0. '
            '2. "explanation": A brief, one-sentence explanation for your reasoning.'
        )
        return {
            'model': self._model_name,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user',   'content': f'Text to analyze:\n---\n{text}\n---'},
            ],
            'stream': False,
        }

    async def _get_prediction_from_api(self, payload: dict) -> dict:
        if self._last_input == payload and self._last_response:
            return self._last_response
        self._last_input = payload

        try:
            resp = await self.client.post('/v1/chat/completions', json=payload)
            resp.raise_for_status()
            content = resp.json()['choices'][0]['message']['content']
            try:
                cleaned = content.strip().replace('```json', '').replace('```', '')
                self._last_response = json.loads(cleaned)
            except json.JSONDecodeError:
                self._last_response = {
                    'hate_speech_probability': 0.0,
                    'explanation': f"Model returned non-JSON: {content[:200]}"
                }
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError, IndexError) as exc:
            print(f"Ollama error ({type(exc).__name__}): {exc}")
            self._last_response = {
                'hate_speech_probability': 0.0,
                'explanation': 'Could not get a valid response from the Ollama service.',
            }

        return self._last_response

    async def predict(self, preprocessed_input: dict) -> float:
        result = await self._get_prediction_from_api(preprocessed_input)
        return result.get('hate_speech_probability', 0.0)

    async def predict_text(self, preprocessed_input: dict) -> str:
        result = await self._get_prediction_from_api(preprocessed_input)
        return result.get('explanation', 'No explanation available.')

    def load(self, model_path: str) -> None:
        pass

    def save(self, model_path: str):
        pass
