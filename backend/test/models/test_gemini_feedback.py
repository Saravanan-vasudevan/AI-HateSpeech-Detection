import unittest
from unittest.mock import patch, MagicMock

from app.models.gemini_feedback import FeedbackGenerator

class TestFeedbackGenerator(unittest.TestCase):
    @patch('models.gemini_feedback.genai')
    def setUp(self, mock_genai):
        self.generator_instance = FeedbackGenerator(name = 'test_generator', api_key = 'fake_api_key')

        self.mock_model = self.generator_instance.model

    @patch('models.gemini_feedback.genai')
    def test_init(self, mock_genai_for_init):
        name       = 'my_feedback_model'
        model_name = 'gemini-test-model'
        api_key    = 'my_secret_key'

        FeedbackGenerator(name = name, model_name = model_name, api_key = api_key)

        mock_genai_for_init.configure.assert_called_once_with(api_key = api_key)

        mock_genai_for_init.GenerativeModel.assert_called_once_with(model_name)

    def test_create_feedback_prompt_correct_scenario(self):
        student_explanation = 'The text used a slur.'
        ai_explanation      = 'The model identified a known slur.'

        prompt = self.generator_instance._create_feedback_prompt(
            student_prediction  = True,
            student_explanation = student_explanation,
            ai_prediction       = True,
            ai_explanation      = ai_explanation
        )

        self.assertIn('encouraging teaching assistant', prompt)

        self.assertIn(f'Student\'s Explanation: "{student_explanation}"', prompt)

        self.assertNotIn('Socratic method', prompt)

    def test_create_feedback_prompt_incorrect_scenario(self):
        student_explanation = 'I just did not like the tone.'
        ai_explanation      = 'The text contained no violating terms.'

        prompt = self.generator_instance._create_feedback_prompt(
            student_prediction  = True,
            student_explanation = student_explanation,
            ai_prediction       = False,
            ai_explanation      = ai_explanation
        )

        self.assertIn('Socratic method', prompt)

        self.assertIn(f'Correct AI\'s Explanation: "{ai_explanation}"', prompt)

        self.assertNotIn('encouraging teaching assistant', prompt)

    def test_generate_success(self):
        mock_api_response = MagicMock()

        mock_api_response.text = '  This is the generated feedback.  '

        self.mock_model.generate_content.return_value = mock_api_response

        result = self.generator_instance.generate(True, 'reason a', True, 'reason b')

        self.assertEqual(result, 'This is the generated feedback.')

        self.mock_model.generate_content.assert_called_once()

    def test_generate_api_error(self):
        self.mock_model.generate_content.side_effect = Exception('Network error')

        result = self.generator_instance.generate(True, 'reason a', True, 'reason b')

        self.assertEqual(result, 'Sorry, I was unable to generate feedback at this time.')

if __name__ == '__main__':
    unittest.main()