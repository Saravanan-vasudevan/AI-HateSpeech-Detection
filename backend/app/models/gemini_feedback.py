from app.models.base_model import BaseModel
import google.generativeai as genai

class FeedbackGenerator(BaseModel):
    '''
    Uses a generative model to provide tailored feedback to a student based on
    their prediction and explanation compared to an AI's output.
    '''
    def __init__(self, name: str, model_name: str = 'gemini-1.5-flash', api_key: str = '') -> None:
        '''
        Initializes the FeedbackGenerator model client.

        Args:
        - name (str)      : A user-friendly name for this model instance.
        - model_name (str): The specific Gemini model to use.
        - api_key (str)   : Key to access the Gemini API.

        Return:
        - None
        '''
        # Constructing the base model
        super().__init__(name)

        # Storing the AI key
        genai.configure(api_key = api_key)

        # Creating the model
        self.model = genai.GenerativeModel(model_name)

    def _create_feedback_prompt(self, student_prediction: bool, student_explanation: str, ai_prediction: bool, ai_explanation: str) -> str:
        '''
        Internal method to create a dynamic prompt based on whether the student was correct.
        
        Input args:
        - student_prediction (bool) : What the student thought the speech was
        - student_explanation (str) : The reason the student thought it was as such
        - ai_prediction (bool)      : What the AI model thought it was
        - ai_explanation (str)      : The reason the AI model it was as such
        '''
        # Scenario 1: The student's prediction was correct.
        if student_prediction == ai_prediction:
            prompt = f"""
            You are an encouraging teaching assistant. A student has correctly identified whether a piece of text is hate speech.
            Your task is to provide positive reinforcement and deepen their understanding.

            - Validate their reasoning in an encouraging way.
            - Briefly add one more point or an alternative perspective to make their understanding more robust.
            - Keep the feedback concise and positive.

            Student's Explanation: "{student_explanation}"
            AI's Explanation (for reference): "{ai_explanation}"

            Generate the feedback now.
            """
        # Scenario 2: The student's prediction was incorrect.
        else:
            prompt = f"""
            You are a helpful tutor using the Socratic method. A student has incorrectly identified whether a piece of text is hate speech.
            Your goal is to guide them to the correct conclusion without giving them the answer directly.

            - Do NOT tell them they are wrong.
            - Analyze both their explanation and the correct explanation.
            - Ask one or two thought-provoking questions that highlight the difference in reasoning and prompt them to reconsider their initial analysis.

            Student's Explanation: "{student_explanation}"
            Correct AI's Explanation: "{ai_explanation}"

            Generate one or two guiding questions now.
            """
        return prompt.strip()

    def generate(self, student_prediction: bool, student_explanation: str, ai_prediction: bool, ai_explanation: str) -> str:
        '''
        Generates feedback for the student.

        Args:
        - student_prediction (bool): The student's classification (True for hate speech).
        - student_explanation (str): The student's reasoning.
        - ai_prediction (bool)     : The AI's classification (True for hate speech).
        - ai_explanation (str)     : The AI's reasoning.

        Returns:
            str: The generated feedback text.
        '''
        # Create the tailored prompt
        prompt = self._create_feedback_prompt(student_prediction, student_explanation, ai_prediction, ai_explanation)

        # Call the API
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            # Fallback in case of an API error
            print(f"An error occurred while generating feedback: {e}")
            return "Sorry, I was unable to generate feedback at this time."

    # These methods are part of the BaseModel contract but are not needed for this class.
    def preprocess(self, text: str):
        pass # Not used directly

    def predict(self, preprocessed_input: str):
        pass # Not used directly

    def predict_text(self, preprocessed_input: str):
        pass # Not used directly

    def load(self, model_path: str):
        print(f"'{self.name}' is a cloud-based API model; no loading is required.")
        pass

    def save(self, model_path: str):
        print(f"'{self.name}' is a cloud-based API model and cannot be saved.")
        pass