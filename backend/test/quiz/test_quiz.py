import unittest
from app.quiz.question import Question 
from app.quiz.quiz import Quiz        

class TestQuiz(unittest.TestCase):
    '''
    Unit tests for the Quiz class.
    '''
    def _create_dummy_question(self, question_text : str = 'Dummy Question?', answers : list = None, 
                               correct_index : int = 0) -> Question:
        '''
        Helper method for the testing that will create a valid
        question for user

        Input args:
        - question_test (str) : The question itself
        - answers (list)      : List of answers to the question
        - correct_index (int) : Number (0th indexed of the answer)

        Return:
        - Question
        '''
        # Checking if answers have been provided
        if answers is None:

            # ... If not, creating dummy question
            answers = ['Option A', 'Option B', 'Option C']

        # Returning valid dummy question
        return Question(question_text, answers, correct_index)

    def test_init_valid_parameters(self):
        '''
        Test that Quiz object is initialized correctly with valid questions.
        '''
        # Creating two dummy questions
        q1 = self._create_dummy_question('Q1?', ['A', 'B'], 0)
        q2 = self._create_dummy_question('Q2?', ['C', 'D'], 1)

        # Putting them in a list for the quiz
        questions = [q1, q2]

        # Creating the quiz
        quiz = Quiz(questions)

        # Check 1 - Is score 0 to start off with?
        self.assertEqual(quiz._score, 0)

        # Check 2  - Do we start at the start of quiz without a question selected?
        self.assertIsNone(quiz._question)

        # Check 3 - Does this correspond to a 0 index for no question?
        self.assertEqual(quiz._index, 0)

        # Check 4 - Have the questions indeed been stored?
        self.assertEqual(quiz._questions, questions) 

    def test_init_raises_type_error_for_non_list(self):
        '''
        Test that __init__ raises TypeError if questions is not a list.
        '''
        # Test 1 - Providing quiz with an input not a string
        with self.assertRaisesRegex(TypeError, 'Questions must be a list.'):
            Quiz('not a list')

        # Test 2 - Providing a null type as the input
        with self.assertRaisesRegex(TypeError, 'Questions must be a list.'):
            Quiz(None)

        # Test 3 - Trying an integer input
        with self.assertRaisesRegex(TypeError, 'Questions must be a list.'):
            Quiz(123)

    def test_init_raises_value_error_for_empty_list(self):
        '''
        Test that __init__ raises ValueError if questions list is empty.
        '''
        # Test - Starting quiz with no inputs
        with self.assertRaisesRegex(ValueError, 'Questions list cannot be empty.'):
            Quiz([])

    def test_init_raises_type_error_for_non_question_objects(self):
        '''
        Test that __init__ raises TypeError if list contains non-Question objects.
        '''
        # Creating a dummy question for helper
        q1 = self._create_dummy_question()

        # Test 1 - Quiz with a question and not a question
        with self.assertRaisesRegex(TypeError, 'All items in the questions list must be Question objects.'):
            Quiz([q1, 'not a question'])

        # Test 2 - Quiz with null and a question
        with self.assertRaisesRegex(TypeError, 'All items in the questions list must be Question objects.'):
            Quiz([None, q1])

        # Test 3 - Not a qustion
        with self.assertRaisesRegex(TypeError, 'All items in the questions list must be Question objects.'):
            Quiz([123])

    def test_has_question_true(self):
        '''
        Test has_question returns True when there are more questions.
        '''
        # Setting up a one-question quiz
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])

        # Test 1 - Does the quiz at least have a question?
        self.assertTrue(quiz.has_question())

        # Retrieving the single quesiton
        quiz.get_question() 

        # Test 2 - Are there now no questions remaining?
        self.assertFalse(quiz.has_question()) 

    def test_has_question_false_empty_quiz(self):
        '''
        Test has_question returns False for an empty quiz (though __init__ prevents this).
        This would be for a quiz that has run out of questions.
        '''
        # Creating a 1 question quiz
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])

        # Consuming the single question
        quiz.get_question() 

        # Test - No questions remain?
        self.assertFalse(quiz.has_question())

    def test_get_question_retrieves_next_question(self):
        '''
        Test that get_question retrieves the correct question and increments index.
        '''
        # Setting up a two question dummy question
        q1 = self._create_dummy_question('First Q?', ['A', 'B'], 0)
        q2 = self._create_dummy_question('Second Q?', ['X', 'Y'], 1)
        quiz = Quiz([q1, q2])

        # First question
        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'First Q?')
        self.assertEqual(answers, ['A', 'B'])
        self.assertEqual(quiz._index, 1)
        self.assertEqual(quiz._question, q1) 

        # Second question
        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'Second Q?')
        self.assertEqual(answers, ['X', 'Y'])
        self.assertEqual(quiz._index, 2)
        self.assertEqual(quiz._question, q2) # Check current _question is set

    def test_get_question_raises_index_error_when_no_more_questions(self):
        '''
        Test that get_question raises IndexError when no more questions are available.
        '''
        # Creating our single-question suiz
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])

        # Retrieving single question
        quiz.get_question() 

        # Test - Checking for error if getting question out of scope
        with self.assertRaisesRegex(IndexError, 'No more questions available in the quiz.'):
            quiz.get_question() 

    def test_get_score_initial(self):
        '''
        Test that get_score returns 0 initially.
        '''
        # Creating a single question quiz
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])

        # Test - Is starting score actually 0?
        self.assertEqual(quiz.get_score(), 0)

    def test_get_score_after_correct_answer(self):
        '''
        Test that get_score increments after a correct answer.
        '''
        # Creating dummy 1-question quiz
        q1 = self._create_dummy_question('Q?', ['A', 'B'], 0)
        quiz = Quiz([q1])
        
        # Retrieving question and providing correct answer
        quiz.get_question() 
        quiz.check_answer(0) 

        # Test - Is score actually 1?
        self.assertEqual(quiz.get_score(), 1)

    def test_get_score_after_incorrect_answer(self):
        '''
        Test that get_score does not increment after an incorrect answer.
        '''
        # Creating 1-question quiz
        q1 = self._create_dummy_question('Q?', ['A', 'B'], 0)
        quiz = Quiz([q1])
        
        # Retrieving and incorrectly answering a question
        quiz.get_question() 
        quiz.check_answer(1) 

        # Test - Checking incorrect answer?
        self.assertEqual(quiz.get_score(), 0)

    def test_check_answer_correct(self):
        '''
        Test check_answer returns True for a correct answer and increments score.
        '''
        # Question - Creating a question but with a different answer
        # This is just to check importance of dummy method
        q1 = self._create_dummy_question('What is 2+2?', ['3', '4', '5'], 1)
        quiz = Quiz([q1])

        # Getting quiz
        quiz.get_question() 
        self.assertTrue(quiz.check_answer(1)) 

        # Check - Is score updating?
        self.assertEqual(quiz.get_score(), 1)

    def test_check_answer_incorrect(self):
        '''
        Test check_answer returns False for an incorrect answer and does not increment score.
        '''
        # Creating question and quiz manually
        q1 = self._create_dummy_question('What is 2+2?', ['3', '4', '5'], 1)
        quiz = Quiz([q1])

        # Storing and incorrect answering question
        quiz.get_question() 
        self.assertFalse(quiz.check_answer(0)) 

        # Test - does score remain 0?
        self.assertEqual(quiz.get_score(), 0)

    def test_check_answer_raises_runtime_error_if_no_question_retrieved(self):
        '''
        Test that check_answer raises RuntimeError if no question has been retrieved yet.
        '''
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])
        
        # Don't call quiz.get_question()
        with self.assertRaisesRegex(RuntimeError, 'No question has been retrieved yet to check an answer against.'):
            quiz.check_answer(0)

    def test_check_answer_raises_type_error_for_non_integer_answer(self):
        '''
        Test that check_answer raises TypeError for non-integer answer input.
        '''
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])
        quiz.get_question() # Retrieve a question first

        # Test 1 - Not integer guess
        with self.assertRaisesRegex(TypeError, 'Answer must be an integer representing the option index.'):
            quiz.check_answer('not an int')

        # Test 2 - Null answer
        with self.assertRaisesRegex(TypeError, 'Answer must be an integer representing the option index.'):
            quiz.check_answer(None)

        # Test 3 - Numeric but not integer test
        with self.assertRaisesRegex(TypeError, 'Answer must be an integer representing the option index.'):
            quiz.check_answer(0.5)

    def test_quiz_flow(self):
        '''
        Test a full simple quiz flow: multiple questions, mixed answers.
        '''
        q1 = self._create_dummy_question('Q1?', ['A', 'B'], 0)
        q2 = self._create_dummy_question('Q2?', ['C', 'D'], 1)
        q3 = self._create_dummy_question('Q3?', ['E', 'F'], 0)
        quiz = Quiz([q1, q2, q3])

        self.assertEqual(quiz.get_score(), 0)
        self.assertTrue(quiz.has_question())

        # Q1: Correct
        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'Q1?')
        self.assertTrue(quiz.check_answer(0))
        self.assertEqual(quiz.get_score(), 1)
        self.assertTrue(quiz.has_question())

        # Q2: Incorrect
        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'Q2?')
        self.assertFalse(quiz.check_answer(0)) # Wrong answer
        self.assertEqual(quiz.get_score(), 1) # Score should remain 1
        self.assertTrue(quiz.has_question())

        # Q3: Correct
        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'Q3?')
        self.assertTrue(quiz.check_answer(0))
        self.assertEqual(quiz.get_score(), 2)
        self.assertFalse(quiz.has_question()) # No more questions

        # Try to get question after quiz ends
        with self.assertRaisesRegex(IndexError, 'No more questions available in the quiz.'):
            quiz.get_question()

        self.assertEqual(quiz.get_score(), 2)


if __name__ == '__main__':
    unittest.main()