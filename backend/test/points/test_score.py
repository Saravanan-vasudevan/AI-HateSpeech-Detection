import unittest
from app.points.score import Score

class TestScore(unittest.TestCase):
    def test_successful_initialization(self):
        username         = 'test_user'
        prediction_score = 100
        quiz_score       = 50

        score = Score(username, prediction_score, quiz_score)

        self.assertEqual(score._username, username)
        self.assertEqual(score._prediction_score, prediction_score)
        self.assertEqual(score._quiz_score, quiz_score)
        self.assertEqual(score.total_score, 150)

        expected_dict = {
            'username'        : 'test_user',
            'prediction_score': 100,
            'quiz_score'      : 50,
            'total_score'     : 150
        }
        self.assertDictEqual(score.to_dict(), expected_dict)


    def test_username_validation(self):
        with self.assertRaisesRegex(TypeError, 'Username must be a string.'):
            Score(username=123, prediction_score=10, quiz_score=10)

        with self.assertRaisesRegex(ValueError, 'Username cannot be empty.'):
            Score(username='', prediction_score=10, quiz_score=10)

        with self.assertRaisesRegex(ValueError, 'Username cannot be empty.'):
            Score(username='   ', prediction_score=10, quiz_score=10)

    def test_score_validation(self):
        with self.assertRaisesRegex(TypeError, 'Prediction score must be a number.'):
            Score(username='test', prediction_score='abc', quiz_score=10)

        with self.assertRaisesRegex(ValueError, 'Prediction score cannot be negative.'):
            Score(username='test', prediction_score=-5, quiz_score=10)

        with self.assertRaisesRegex(TypeError, 'Quiz score must be a number.'):
            Score(username='test', prediction_score=10, quiz_score='xyz')

        with self.assertRaisesRegex(ValueError, 'Quiz score cannot be negative.'):
            Score(username='test', prediction_score=10, quiz_score=-1)

if __name__ == '__main__':
    unittest.main()