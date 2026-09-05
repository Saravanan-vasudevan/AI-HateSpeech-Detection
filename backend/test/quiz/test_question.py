import unittest
from app.quiz.question import Question

class TestQuestion(unittest.TestCase):
    def test_init_valid_parameters(self) -> None:
        question_text        = 'What is the capital of France?'
        answers_list         = ['Berlin', 'Madrid', 'Paris', 'Rome']
        correct_answer_index = 2

        q = Question(question_text, answers_list, correct_answer_index)

        self.assertEqual(q.get_question(), question_text)
        self.assertEqual(q.get_answers(), answers_list)
        self.assertEqual(q.get_answer(), correct_answer_index)

    def test_init_invalid_question_text(self) -> None:
        with self.assertRaisesRegex(ValueError, 'Question must be a non-empty string.'):
            Question(None, ['A'], 0)

        with self.assertRaisesRegex(ValueError, 'Question must be a non-empty string.'):
            Question('', ['A'], 0)

        with self.assertRaisesRegex(ValueError, "Question must be a non-empty string."):
            Question('   ', ['A'], 0)

        with self.assertRaisesRegex(ValueError, "Question must be a non-empty string."):
            Question(123, ['A'], 0)

    def test_init_invalid_answers_list(self):
        with self.assertRaisesRegex(ValueError, 'Answers must be a non-empty list.'):
            Question('Q?', None, 0)

        with self.assertRaisesRegex(ValueError, 'Answers must be a non-empty list.'):
            Question('Q', [], 0)

        with self.assertRaisesRegex(ValueError, 'Answers must be a non-empty list.'):
            Question('Q?', 'not a list', 0)

    def test_init_invalid_answer_list_elements(self):
        with self.assertRaisesRegex(ValueError, 'All answers in the list must be non-empty strings.'):
            Question('Q?', ['A', 123], 0)

        with self.assertRaisesRegex(ValueError, 'All answers in the list must be non-empty strings.'):
            Question('Q?', ['A', ''], 0)

        with self.assertRaisesRegex(ValueError, 'All answers in the list must be non-empty strings.'):
            Question('Q?', ['A', '   '], 0)

    def test_init_invalid_answer_index_type(self):
        with self.assertRaisesRegex(TypeError, 'Answer index must be an integer.'):
            Question('Q?', ['A', 'B'], '0')

        with self.assertRaisesRegex(TypeError, 'Answer index must be an integer.'):
            Question('Q?', ['A', 'B'], 0.5)

    def test_init_invalid_answer_index_out_of_bounds(self):
        with self.assertRaisesRegex(IndexError, 'Answer index is out of bounds for the provided answers.'):
            Question('Q?', ['A', 'B'], 2)

        with self.assertRaisesRegex(IndexError, 'Answer index is out of bounds for the provided answers.'):
            Question('Q?', ['A', 'B'], -1)
    def test_get_question(self):
        q = Question('Test question?', ['Yes', 'No'], 0)

        self.assertEqual(q.get_question(), "Test question?")

    def test_get_answers(self):
        answers = ['Option A', 'Option B']

        q = Question('Test question?', answers, 0)

        self.assertEqual(q.get_answers(), answers)


    def test_get_answer(self):
        q = Question('Test question?', ['A', 'B', 'C'], 1)

        self.assertEqual(q.get_answer(), 1)

    def test_is_correct_true(self):
        q = Question('What is 1+1?', ['1', '2', '3'], 1)

        self.assertTrue(q.is_correct(1))

    def test_is_correct_false(self):
        q = Question('What is 1+1?', ['1', '2', '3'], 1)

        self.assertFalse(q.is_correct(0))

        self.assertFalse(q.is_correct(2))

    def test_is_correct_invalid_input(self):
        q = Question('Q', ['A', 'B'], 0)

        self.assertFalse(q.is_correct('not an int'))

        self.assertFalse(q.is_correct(None))

        self.assertFalse(q.is_correct(0.5))

if __name__ == '__main__':
    unittest.main()
