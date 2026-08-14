import unittest
from app.quiz.quiz import Question 

class TestQuestion(unittest.TestCase):
    '''
    Unit tests for the Question class.
    To ensure accurate functionality from a coding
    perspective
    '''
    def test_init_valid_parameters(self) -> None:
        '''
        Test that the Question object is initialized correctly with valid parameters.
        
        Input args:
        - None
        
        Return:
        - None
        '''
        # Example 1 - Valid question
        question_text        = 'What is the capital of France?'
        answers_list         = ['Berlin', 'Madrid', 'Paris', 'Rome']
        correct_answer_index = 2
        
        # Creating the question object
        q = Question(question_text, answers_list, correct_answer_index)
        
        # Checking the attributes are correctly stored
        self.assertEqual(q.get_question(), question_text)
        self.assertEqual(q.get_answers(), answers_list)
        self.assertEqual(q.get_answer(), correct_answer_index)

    def test_init_invalid_question_text(self) -> None:
        '''
        Test that __init__ raises ValueError for invalid question text.

        Input args:
        - None

        Return:
        - None
        '''
        # Test 1 - Does is check for an empty question prompt?
        with self.assertRaisesRegex(ValueError, 'Question must be a non-empty string.'):
            Question(None, ['A'], 0)

        # Test 2 - Does it check for a null string?
        with self.assertRaisesRegex(ValueError, 'Question must be a non-empty string.'):
            Question('', ['A'], 0)

        # Test 3 - Does it check for a string with no characters?
        with self.assertRaisesRegex(ValueError, "Question must be a non-empty string."):
            Question('   ', ['A'], 0)

        # Test 4 - Does it pick a non-string input?
        with self.assertRaisesRegex(ValueError, "Question must be a non-empty string."):
            Question(123, ['A'], 0) 

    def test_init_invalid_answers_list(self):
        '''
        Test that __init__ raises ValueError for invalid answers list.
        '''
        # Check 1 - Does it pick up no input to questions?
        with self.assertRaisesRegex(ValueError, 'Answers must be a non-empty list.'):
            Question('Q?', None, 0)

        # Check 2 - Does it pick up an empty list?
        with self.assertRaisesRegex(ValueError, 'Answers must be a non-empty list.'):
            Question('Q', [], 0)

        # Check 3 - Does it pick a data type not a list?
        with self.assertRaisesRegex(ValueError, 'Answers must be a non-empty list.'):
            Question('Q?', 'not a list', 0)

    def test_init_invalid_answer_list_elements(self):
        '''
        Test that __init__ raises ValueError if answers list contains non-string or empty elements.
        '''
        # Test 1 - Adding a non-string option
        with self.assertRaisesRegex(ValueError, 'All answers in the list must be non-empty strings.'):
            Question('Q?', ['A', 123], 0) 

        # Test 2 - Adding a null string as an option?
        with self.assertRaisesRegex(ValueError, 'All answers in the list must be non-empty strings.'):
            Question('Q?', ['A', ''], 0) 

        # Test 3 - Adding a longer string with no character?
        with self.assertRaisesRegex(ValueError, 'All answers in the list must be non-empty strings.'):
            Question('Q?', ['A', '   '], 0) 

    def test_init_invalid_answer_index_type(self):
        '''
        Test that __init__ raises TypeError for non-integer answer index.
        '''
        # Test 1 - Non-integer, non-numeric answer argument
        with self.assertRaisesRegex(TypeError, 'Answer index must be an integer.'):
            Question('Q?', ['A', 'B'], '0')

        # Test 2 - Numeric but non-integer value
        with self.assertRaisesRegex(TypeError, 'Answer index must be an integer.'):
            Question('Q?', ['A', 'B'], 0.5)

    def test_init_invalid_answer_index_out_of_bounds(self):
        '''
        Test that __init__ raises IndexError for out-of-bounds answer index.
        '''
        # Check 1 - Answer out of range
        with self.assertRaisesRegex(IndexError, 'Answer index is out of bounds for the provided answers.'):
            Question('Q?', ['A', 'B'], 2) 

        # Check 2 - Answer out range but in a negative direction
        with self.assertRaisesRegex(IndexError, 'Answer index is out of bounds for the provided answers.'):
            Question('Q?', ['A', 'B'], -1) 
    def test_get_question(self):
        '''
        Test that get_question returns the correct question text.
        '''
        # Setting the dummy question
        q = Question('Test question?', ['Yes', 'No'], 0)

        # Checking correct question prompt
        self.assertEqual(q.get_question(), "Test question?")

    def test_get_answers(self):
        '''
        Test that get_answers returns the correct list of answers.
        '''
        # Setting the answers first
        answers = ['Option A', 'Option B']

        # Setting the question by adding the answers
        q = Question('Test question?', answers, 0)

        # Checking answers are correct
        self.assertEqual(q.get_answers(), answers)


    def test_get_answer(self):
        '''
        Test that get_answer returns the correct index of the correct answer.
        '''
        # Setting up dummy question
        q = Question('Test question?', ['A', 'B', 'C'], 1)

        # Checking correct answer is indeed 1
        self.assertEqual(q.get_answer(), 1)

    def test_is_correct_true(self):
        '''
        Test that is_correct returns True for the correct answer.
        '''
        # Question with correct first option
        q = Question('What is 1+1?', ['1', '2', '3'], 1)

        # Check - Is the first option indeed correct?
        self.assertTrue(q.is_correct(1))

    def test_is_correct_false(self):
        '''
        Test that is_correct returns False for an incorrect answer.
        '''
        # Constructing the question
        q = Question('What is 1+1?', ['1', '2', '3'], 1)

        # Check 1 - Incorrect answer one
        self.assertFalse(q.is_correct(0))

        # Check 2 - Incorrect answer two
        self.assertFalse(q.is_correct(2))

    def test_is_correct_invalid_input(self):
        '''
        Test that is_correct handles invalid input types gracefully (returns False).
        '''
        # Constructing my question
        q = Question('Q', ['A', 'B'], 0)

        # Check 1 - Does not fall over with string input?
        self.assertFalse(q.is_correct('not an int'))

        # Check 2 - Does not fall over with null type?
        self.assertFalse(q.is_correct(None))

        # Check 3 - A non-integer, numeric value?
        self.assertFalse(q.is_correct(0.5))

if __name__ == '__main__':
    unittest.main()