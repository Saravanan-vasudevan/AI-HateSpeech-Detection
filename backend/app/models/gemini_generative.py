from app.models.base_model import BaseModel
import google.generativeai as genai
import json


class GeminiHateSpeechModel(BaseModel):
    """Wraps the Gemini API for hate speech classification.

    We ask Gemini to return structured JSON with a probability and a short
    explanation.  The response is cached per-input so back-to-back calls
    to predict() and predict_text() with the same prompt don't double-bill.
    """

    def __init__(self, name: str, model_name: str = 'gemini-1.5-flash',
                 api_key: str = '') -> None:
        super().__init__(name)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self._last_input    = None
        self._last_response = None

    def preprocess(self, text: str) -> str:
        """Build the structured prompt that asks Gemini for JSON output."""
        return f"""
You are a content moderation expert. Analyze the following text for hate speech.
Respond ONLY with a valid JSON object. The JSON object must contain two keys:
1. "hate_speech_probability": A float between 0.0 (not hate speech) and 1.0 (definitely hate speech).
2. "explanation": A brief, one-sentence explanation for your reasoning.

Text to analyze:
---
{text}
---""".strip()

    def _get_prediction_from_api(self, prompt: str) -> dict:
        """Call the API (or return the cached result for the same prompt)."""
        if self._last_input == prompt and self._last_response:
            return self._last_response

        response = self.model.generate_content(prompt)
        self._last_input = prompt

        try:
            raw = response.text.strip().replace('```json', '').replace('```', '')
            self._last_response = json.loads(raw)
        except (json.JSONDecodeError, AttributeError):
            self._last_response = {
                'hate_speech_probability': 0.0,
                'explanation': 'Error: Could not parse model output.',
            }
        return self._last_response

    def predict(self, preprocessed_input: str) -> float:
        return self._get_prediction_from_api(preprocessed_input).get(
            'hate_speech_probability', 0.0)

    def predict_text(self, preprocessed_input: str) -> str:
        return self._get_prediction_from_api(preprocessed_input).get(
            'explanation', 'No explanation available.')

    def load(self, model_path: str) -> None:
        pass

    def save(self, model_path: str):
        pass
