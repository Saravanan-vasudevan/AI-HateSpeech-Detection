from app.models.base_model import BaseModel
import google.generativeai as genai


class FeedbackGenerator(BaseModel):
    """Uses Gemini to generate pedagogical feedback comparing a student's
    hate-speech classification against the AI's.

    Two prompt templates:
      - Student got it right  -> positive reinforcement + one extra insight.
      - Student got it wrong  -> Socratic questions to guide them, no answer.
    """

    def __init__(self, name: str, model_name: str = 'gemini-1.5-flash',
                 api_key: str = '') -> None:
        super().__init__(name)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def _build_prompt(self, student_prediction, student_explanation,
                      ai_prediction, ai_explanation) -> str:
        if student_prediction == ai_prediction:
            return f"""
You are an encouraging teaching assistant. A student has correctly identified whether a piece of text is hate speech.
Your task is to provide positive reinforcement and deepen their understanding.

- Validate their reasoning in an encouraging way.
- Briefly add one more point or an alternative perspective to make their understanding more robust.
- Keep the feedback concise and positive.

Student's Explanation: "{student_explanation}"
AI's Explanation (for reference): "{ai_explanation}"

Generate the feedback now.""".strip()
        else:
            return f"""
You are a helpful tutor using the Socratic method. A student has incorrectly identified whether a piece of text is hate speech.
Your goal is to guide them to the correct conclusion without giving them the answer directly.

- Do NOT tell them they are wrong.
- Analyze both their explanation and the correct explanation.
- Ask one or two thought-provoking questions that highlight the difference in reasoning and prompt them to reconsider their initial analysis.

Student's Explanation: "{student_explanation}"
Correct AI's Explanation: "{ai_explanation}"

Generate one or two guiding questions now.""".strip()

    def generate(self, student_prediction: bool, student_explanation: str,
                 ai_prediction: bool, ai_explanation: str) -> str:
        """Call Gemini with the appropriate prompt template and return the
        feedback text, or a fallback message on failure."""
        prompt = self._build_prompt(student_prediction, student_explanation,
                                    ai_prediction, ai_explanation)
        try:
            resp = self.model.generate_content(prompt)
            return resp.text.strip()
        except Exception as e:
            print(f"Feedback generation error: {e}")
            return "Sorry, I was unable to generate feedback at this time."

    def preprocess(self, text):   pass
    def predict(self, inp):       pass
    def predict_text(self, inp):  pass
    def load(self, path):         pass
    def save(self, path):         pass
