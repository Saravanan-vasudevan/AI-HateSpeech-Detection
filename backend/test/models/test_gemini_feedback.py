# Import standard libraries
import unittest
from unittest.mock import patch, MagicMock

# Import the class to be tested
from app.models.gemini_feedback import FeedbackGenerator

class TestFeedbackGenerator(unittest.TestCase):
    '''
    Contains all unit tests for the FeedbackGenerator class using the unittest framework.
    '''
    # This method runs before each test function
    @patch('models.gemini_feedback.genai')
    def setUp(self, mock_genai):
        '''
        Sets up a test environment before each test.
        This method creates a fresh instance of FeedbackGenerator and a mock of the
        'genai' library for each test function.
        '''
        # Create an instance of the class to be used by the tests
        self.generator_instance = FeedbackGenerator(name = 'test_generator', api_key = 'fake_api_key')

        # Mocking the model to check it later
        self.mock_model = self.generator_instance.model

    # Test to ensure the class initializes correctly
    @patch('models.gemini_feedback.genai')
    def test_init(self, mock_genai_for_init):
        '''
        Tests if the __init__ method correctly configures the genai client
        and initializes the GenerativeModel.
        '''
        # Define mock arguments
        name       = 'my_feedback_model'
        model_name = 'gemini-test-model'
        api_key    = 'my_secret_key'

        # Call the constructor
        FeedbackGenerator(name = name, model_name = model_name, api_key = api_key)

        # Assert that the genai module was configured with the API key
        mock_genai_for_init.configure.assert_called_once_with(api_key = api_key)

        # Assert that the generative model was instantiated with the correct model name
        mock_genai_for_init.GenerativeModel.assert_called_once_with(model_name)

    # Test the prompt creation logic for a correct student answer
    def test_create_feedback_prompt_correct_scenario(self):
        '''
        Tests the _create_feedback_prompt method when the student and AI predictions match.
        The prompt should be encouraging.
        '''
        # Define inputs for a correct scenario
        student_explanation = 'The text used a slur.'
        ai_explanation      = 'The model identified a known slur.'

        # Generate the prompt using the instance created in setUp
        prompt = self.generator_instance._create_feedback_prompt(
            student_prediction  = True,
            student_explanation = student_explanation,
            ai_prediction       = True,
            ai_explanation      = ai_explanation
        )

        # Assert that the prompt contains keywords for the "correct" template
        self.assertIn('encouraging teaching assistant', prompt)

        # Assert that the student's explanation is included
        self.assertIn(f'Student\'s Explanation: "{student_explanation}"', prompt)

        # Assert that keywords for the "incorrect" template are absent
        self.assertNotIn('Socratic method', prompt)

    # Test the prompt creation logic for an incorrect student answer
    def test_create_feedback_prompt_incorrect_scenario(self):
        '''
        Tests the _create_feedback_prompt method when the student and AI predictions differ.
        The prompt should be Socratic and guiding.
        '''
        # Define inputs for an incorrect scenario
        student_explanation = 'I just did not like the tone.'
        ai_explanation      = 'The text contained no violating terms.'

        # Generate the prompt
        prompt = self.generator_instance._create_feedback_prompt(
            student_prediction  = True,
            student_explanation = student_explanation,
            ai_prediction       = False,
            ai_explanation      = ai_explanation
        )

        # Assert that the prompt contains keywords for the "incorrect" template
        self.assertIn('Socratic method', prompt)

        # Assert that the AI's explanation is included as the correct one
        self.assertIn(f'Correct AI\'s Explanation: "{ai_explanation}"', prompt)

        # Assert that keywords for the "correct" template are absent
        self.assertNotIn('encouraging teaching assistant', prompt)

    # Test the main 'generate' method for a successful API call
    def test_generate_success(self):
        '''
        Tests the generate method for a successful API call, ensuring it returns
        the cleaned text from the model's response.
        '''
        # Create a mock response object that the fake API call will return
        mock_api_response = MagicMock()

        # Set the text attribute on the mock response, including extra whitespace
        mock_api_response.text = '  This is the generated feedback.  '
        
        # Configure the mocked model (from setUp) to return our mock response
        self.mock_model.generate_content.return_value = mock_api_response

        # Call the method being tested
        result = self.generator_instance.generate(True, 'reason a', True, 'reason b')

        # Assert that the returned result is the stripped text
        self.assertEqual(result, 'This is the generated feedback.')
        
        # Assert that the API was called exactly once
        self.mock_model.generate_content.assert_called_once()

    # Test the 'generate' method for a failed API call
    def test_generate_api_error(self):
        '''
        Tests the generate method's error handling when the API call fails.
        It should return a user-friendly error message.
        '''
        # Configure the mocked model to raise an exception when called
        self.mock_model.generate_content.side_effect = Exception('Network error')

        # Call the method being tested
        result = self.generator_instance.generate(True, 'reason a', True, 'reason b')

        # Assert that the method returns the fallback error message
        self.assertEqual(result, 'Sorry, I was unable to generate feedback at this time.')

# This allows the test to be run from the command line
if __name__ == '__main__':
    unittest.main()