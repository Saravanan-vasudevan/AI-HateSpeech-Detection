import unittest
from app.points.score import Score

class TestScore(unittest.TestCase):
    '''
    Test suite for the Score class to ensure its logic and validation are correct.
    '''
    def test_successful_initialization(self):
        '''
        Tests that a Score object is created correctly with valid inputs
        and that its properties and methods work as expected.
        '''
        # Define valid inputs for the Score object.
        username         = 'test_user'
        prediction_score = 100
        quiz_score       = 50

        # Create an instance of the Score class.
        score = Score(username, prediction_score, quiz_score)

        # Assert: Check that the object's state and methods are correct.
        self.assertEqual(score._username, username)
        self.assertEqual(score._prediction_score, prediction_score)
        self.assertEqual(score._quiz_score, quiz_score)
        self.assertEqual(score.total_score, 150)

        # Assert that the dictionary output is correct.
        expected_dict = {
            'username'        : 'test_user',
            'prediction_score': 100,
            'quiz_score'      : 50,
            'total_score'     : 150
        }
        self.assertDictEqual(score.to_dict(), expected_dict)


    def test_username_validation(self):
        '''
        Tests that the appropriate errors are raised for invalid usernames.
        '''
        # Assert that a TypeError is raised for a non-string username.
        with self.assertRaisesRegex(TypeError, 'Username must be a string.'):
            Score(username=123, prediction_score=10, quiz_score=10)

        # Assert that a ValueError is raised for an empty string username.
        with self.assertRaisesRegex(ValueError, 'Username cannot be empty.'):
            Score(username='', prediction_score=10, quiz_score=10)
        
        # Assert that a ValueError is raised for a whitespace-only username.
        with self.assertRaisesRegex(ValueError, 'Username cannot be empty.'):
            Score(username='   ', prediction_score=10, quiz_score=10)

    def test_score_validation(self):
        '''
        Tests that the appropriate errors are raised for invalid score values.
        '''
        # Assert TypeError for a non-numeric prediction score.
        with self.assertRaisesRegex(TypeError, 'Prediction score must be a number.'):
            Score(username='test', prediction_score='abc', quiz_score=10)

        # Assert ValueError for a negative prediction score.
        with self.assertRaisesRegex(ValueError, 'Prediction score cannot be negative.'):
            Score(username='test', prediction_score=-5, quiz_score=10)

        # Assert TypeError for a non-numeric quiz score.
        with self.assertRaisesRegex(TypeError, 'Quiz score must be a number.'):
            Score(username='test', prediction_score=10, quiz_score='xyz')

        # Assert ValueError for a negative quiz score.
        with self.assertRaisesRegex(ValueError, 'Quiz score cannot be negative.'):
            Score(username='test', prediction_score=10, quiz_score=-1)

if __name__ == '__main__':
    unittest.main()