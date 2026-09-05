import unittest
from app.quiz.question import Question
from app.quiz.quiz import Quiz

class TestQuiz(unittest.TestCase):
    def _create_dummy_question(self, question_text : str = 'Dummy Question?', answers : list = None,
                               correct_index : int = 0) -> Question:
        if answers is None:

            answers = ['Option A', 'Option B', 'Option C']

        return Question(question_text, answers, correct_index)

    def test_init_valid_parameters(self):
        q1 = self._create_dummy_question('Q1?', ['A', 'B'], 0)
        q2 = self._create_dummy_question('Q2?', ['C', 'D'], 1)

        questions = [q1, q2]

        quiz = Quiz(questions)

        self.assertEqual(quiz._score, 0)

        self.assertIsNone(quiz._question)

        self.assertEqual(quiz._index, 0)

        self.assertEqual(quiz._questions, questions)

    def test_init_raises_type_error_for_non_list(self):
        with self.assertRaisesRegex(TypeError, 'Questions must be a list.'):
            Quiz('not a list')

        with self.assertRaisesRegex(TypeError, 'Questions must be a list.'):
            Quiz(None)

        with self.assertRaisesRegex(TypeError, 'Questions must be a list.'):
            Quiz(123)

    def test_init_raises_value_error_for_empty_list(self):
        with self.assertRaisesRegex(ValueError, 'Questions list cannot be empty.'):
            Quiz([])

    def test_init_raises_type_error_for_non_question_objects(self):
        q1 = self._create_dummy_question()

        with self.assertRaisesRegex(TypeError, 'All items in the questions list must be Question objects.'):
            Quiz([q1, 'not a question'])

        with self.assertRaisesRegex(TypeError, 'All items in the questions list must be Question objects.'):
            Quiz([None, q1])

        with self.assertRaisesRegex(TypeError, 'All items in the questions list must be Question objects.'):
            Quiz([123])

    def test_has_question_true(self):
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])

        self.assertTrue(quiz.has_question())

        quiz.get_question()

        self.assertFalse(quiz.has_question())

    def test_has_question_false_empty_quiz(self):
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])

        quiz.get_question()

        self.assertFalse(quiz.has_question())

    def test_get_question_retrieves_next_question(self):
        q1 = self._create_dummy_question('First Q?', ['A', 'B'], 0)
        q2 = self._create_dummy_question('Second Q?', ['X', 'Y'], 1)
        quiz = Quiz([q1, q2])

        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'First Q?')
        self.assertEqual(answers, ['A', 'B'])
        self.assertEqual(quiz._index, 1)
        self.assertEqual(quiz._question, q1)

        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'Second Q?')
        self.assertEqual(answers, ['X', 'Y'])
        self.assertEqual(quiz._index, 2)
        self.assertEqual(quiz._question, q2)

    def test_get_question_raises_index_error_when_no_more_questions(self):
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])

        quiz.get_question()

        with self.assertRaisesRegex(IndexError, 'No more questions available in the quiz.'):
            quiz.get_question()

    def test_get_score_initial(self):
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])

        self.assertEqual(quiz.get_score(), 0)

    def test_get_score_after_correct_answer(self):
        q1 = self._create_dummy_question('Q?', ['A', 'B'], 0)
        quiz = Quiz([q1])

        quiz.get_question()
        quiz.check_answer(0)

        self.assertEqual(quiz.get_score(), 1)

    def test_get_score_after_incorrect_answer(self):
        q1 = self._create_dummy_question('Q?', ['A', 'B'], 0)
        quiz = Quiz([q1])

        quiz.get_question()
        quiz.check_answer(1)

        self.assertEqual(quiz.get_score(), 0)

    def test_check_answer_correct(self):
        q1 = self._create_dummy_question('What is 2+2?', ['3', '4', '5'], 1)
        quiz = Quiz([q1])

        quiz.get_question()
        self.assertTrue(quiz.check_answer(1))

        self.assertEqual(quiz.get_score(), 1)

    def test_check_answer_incorrect(self):
        q1 = self._create_dummy_question('What is 2+2?', ['3', '4', '5'], 1)
        quiz = Quiz([q1])

        quiz.get_question()
        self.assertFalse(quiz.check_answer(0))

        self.assertEqual(quiz.get_score(), 0)

    def test_check_answer_raises_runtime_error_if_no_question_retrieved(self):
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])

        with self.assertRaisesRegex(RuntimeError, 'No question has been retrieved yet to check an answer against.'):
            quiz.check_answer(0)

    def test_check_answer_raises_type_error_for_non_integer_answer(self):
        q1 = self._create_dummy_question()
        quiz = Quiz([q1])
        quiz.get_question()

        with self.assertRaisesRegex(TypeError, 'Answer must be an integer representing the option index.'):
            quiz.check_answer('not an int')

        with self.assertRaisesRegex(TypeError, 'Answer must be an integer representing the option index.'):
            quiz.check_answer(None)

        with self.assertRaisesRegex(TypeError, 'Answer must be an integer representing the option index.'):
            quiz.check_answer(0.5)

    def test_quiz_flow(self):
        q1 = self._create_dummy_question('Q1?', ['A', 'B'], 0)
        q2 = self._create_dummy_question('Q2?', ['C', 'D'], 1)
        q3 = self._create_dummy_question('Q3?', ['E', 'F'], 0)
        quiz = Quiz([q1, q2, q3])

        self.assertEqual(quiz.get_score(), 0)
        self.assertTrue(quiz.has_question())

        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'Q1?')
        self.assertTrue(quiz.check_answer(0))
        self.assertEqual(quiz.get_score(), 1)
        self.assertTrue(quiz.has_question())

        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'Q2?')
        self.assertFalse(quiz.check_answer(0))
        self.assertEqual(quiz.get_score(), 1)
        self.assertTrue(quiz.has_question())

        q_text, answers = quiz.get_question()
        self.assertEqual(q_text, 'Q3?')
        self.assertTrue(quiz.check_answer(0))
        self.assertEqual(quiz.get_score(), 2)
        self.assertFalse(quiz.has_question())

        with self.assertRaisesRegex(IndexError, 'No more questions available in the quiz.'):
            quiz.get_question()

        self.assertEqual(quiz.get_score(), 2)


if __name__ == '__main__':
    unittest.main()