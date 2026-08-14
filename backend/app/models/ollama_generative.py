from app.models.base_model import BaseModel
import httpx
import json
import os

class OllamaModel(BaseModel):
    '''
    A generative model that interacts with a self-hosted Ollama API endpoint,
    such as one deployed on Google Cloud Run.
    '''
    def __init__(self, name: str, model_name: str = 'llama3', api_url: str = ''):
        '''
        Initializes the client for the self-hosted Ollama model.

        Args:
        - name (str)      : A user-friendly name for this model instance.
        - model_name (str): The specific Ollama model to use (e.g., 'llama3').
        - api_url (str)   : The base URL of the deployed Ollama service.

        Raises:
        - ValueError: If the api_url is not provided.

        Return:
        - None
        '''
        # Call the parent class constructor.
        super().__init__(name)

        # Ensure the API URL is provided.
        if not api_url:
            raise ValueError('OLLAMA_API_URL must be provided for the OllamaModel.')

        # Store the model name and API URL.
        self._model_name = model_name
        self._api_url = api_url

        # Initialize an asynchronous HTTP client for making API calls.
        self.client = httpx.AsyncClient(base_url = self._api_url, timeout = 300.0)

        # Store the last input and parsed response for simple caching.
        self._last_input    = None
        self._last_response = None

    # Prepares the JSON payload for the Ollama API.
    def preprocess(self, text: str) -> dict:
        '''
        Creates the full JSON payload required by the Ollama OpenAI-compatible API.
        
        Args:
        - text (str): The raw text to analyze.
        
        Returns:
        - dict: The dictionary payload ready to be sent to the API.
        '''
        # The system prompt instructs the model on its role and desired output format.
        system_prompt = (
            'You are a content moderation expert. Analyze the following text for hate speech. '
            'Respond ONLY with a valid JSON object. The JSON object must contain two keys: '
            '1. "hate_speech_probability": A float between 0.0 and 1.0. '
            '2. "explanation": A brief, one-sentence explanation for your reasoning.'
        )

        # The user prompt contains the text to be analyzed.
        user_prompt = f'Text to analyze:\n---\n{text}\n---'

        # Construct the final request body.
        request_body = {
            'model': self._model_name,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'stream': False
        }
        return request_body

    async def _get_prediction_from_api(self, preprocessed_input: dict) -> dict:
        '''
        Internal async method to call the Ollama API and parse the JSON response.
        '''
        # Check - Has the input already been cached?
        if self._last_input == preprocessed_input and self._last_response:
            return self._last_response

        # Else, procssing the input
        self._last_input = preprocessed_input

        # Performing the analysis
        try:

            # .... Posting to model
            response = await self.client.post('/v1/chat/completions', json = preprocessed_input)
            response.raise_for_status()
            
            # ... Formatting as JSON
            response_data = response.json()
            message_content = response_data['choices'][0]['message']['content']
            
            # Cleaning JSON
            try:
                # First, try to parse the content as JSON after cleaning it.
                clean_json_str = message_content.strip().replace('```json', '').replace('```', '')
                self._last_response = json.loads(clean_json_str)

            except json.JSONDecodeError:
                # If parsing fails, it's likely a safety refusal or conversational text.
                # We'll treat this as "not hate speech" and use the model's raw message as the explanation.
                self._last_response = {
                    'hate_speech_probability': 0.0,
                    'explanation': f"Model Refusal: {message_content}"
                }
                

        # Enhanced error printings
        except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, KeyError, IndexError) as e:
            
            # Print the actual error to the terminal for debugging
            print(f"\n--- OLLAMA MODEL ERROR ---")
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Error details: {e}")

            # Also print the raw response if possible
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"Raw Response Text: {response.text}")
            print(f"--------------------------\n")
            
            # The rest of the block remains the same
            self._last_response = {
                'hate_speech_probability': 0.0,
                'explanation': 'Error: Could not get a valid response from the Ollama service.'
            }
        
        return self._last_response

    # Predicts the probability of hate speech.
    async def predict(self, preprocessed_input: dict) -> float:
        '''
        Predicts the probability of the text being hate speech.
        '''
        # Call the internal method to get the parsed API response.
        response_dict = await self._get_prediction_from_api(preprocessed_input)

        # Return the probability, defaulting to 0.0 if not found.
        return response_dict.get('hate_speech_probability', 0.0)

    # Gets the model's textual explanation.
    async def predict_text(self, preprocessed_input: dict) -> str:
        '''
        Gets the model's textual explanation for its prediction.
        '''
        # Call the internal method to get the parsed API response.
        response_dict = await self._get_prediction_from_api(preprocessed_input)
        
        # Return the explanation, defaulting if not found.
        return response_dict.get('explanation', 'No explanation available.')

    # No-op method as the model is a remote service.
    def load(self, model_path: str) -> None:
        '''No-op: The model is a cloud-based API and does not need to be loaded from a file.'''
        print(f"'{self.name}' is a remote API model; no loading is required.")
        pass

    # No-op method as the model is a remote service.
    def save(self, model_path: str):
        '''No-op: The model is a remote API and cannot be saved to a file.'''
        print(f"'{self.name}' is a remote API model and cannot be saved.")
        pass