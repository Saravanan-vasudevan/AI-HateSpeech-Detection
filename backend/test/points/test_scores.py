import unittest
from app.points.score import Score
from app.points.scores import Scores


class TestScores(unittest.TestCase):
    '''
    A test suite for the Scores collection class to ensure its logic
    and validation are working correctly.
    '''
    # This method runs before each test, setting up common objects.
    def setUp(self):
        '''
        Set up some common Score objects to be used across multiple tests.
        '''
        # Arrange: Create a few Score objects with different total scores.
        self.score_low  = Score(username='user_c', prediction_score=10, quiz_score=10)    # Total: 20
        self.score_high = Score(username='user_a', prediction_score=50, quiz_score=50)   # Total: 100
        self.score_mid  = Score(username='user_b', prediction_score=25, quiz_score=25)    # Total: 50

    # Tests for object initialization.
    def test_initialization(self):
        '''
        Tests both empty initialization and initialization with a valid list.
        '''
        # Test creating an empty Scores object.
        scores_empty = Scores()
        self.assertEqual(len(scores_empty), 0)

        # Test creating a Scores object with a valid list.
        scores_populated = Scores(initial_scores = [self.score_low, self.score_high])
        self.assertEqual(len(scores_populated), 2)
        self.assertIn(self.score_low, scores_populated)

    # Tests for validation during initialization.
    def test_initialization_validation(self):
        '''
        Tests that initialization raises appropriate errors for invalid input.
        '''
        # Assert TypeError if initial_scores is not a list.
        with self.assertRaisesRegex(TypeError, 'initial_scores must be a list'):
            Scores(initial_scores='not-a-list')

        # Assert TypeError if the list contains non-Score objects.
        with self.assertRaisesRegex(TypeError, 'Only Score objects can be added'):
            Scores(initial_scores=[self.score_low, 123, self.score_high])

    # Test for the add_score method.
    def test_add_score_method(self):
        '''
        Tests adding a valid Score and validates rejection of invalid types.
        '''
        # Arrange: Create an empty Scores object.
        scores = Scores()
        
        # Act: Add a valid Score.
        scores.add_score(self.score_mid)
        
        # Assert: Check the score was added.
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0], self.score_mid)
        
        # Assert that adding a non-Score object raises a TypeError.
        with self.assertRaisesRegex(TypeError, 'Only Score objects can be added'):
            scores.add_score('a-random-string')
        
        # Assert that the invalid object was not added.
        self.assertEqual(len(scores), 1)
        
    # Test for the primary get_leaderboard method.
    def test_get_leaderboard(self):
        '''
        Tests that get_leaderboard returns a list of Score objects
        sorted correctly by total_score in descending order.
        '''
        # Arrange: Create a Scores object with unsorted scores.
        scores = Scores(initial_scores=[self.score_low, self.score_high, self.score_mid])
        
        # Define the expected order: high (100), mid (50), low (20).
        expected_order = [self.score_high, self.score_mid, self.score_low]
        
        # Act: Get the leaderboard.
        leaderboard = scores.get_leaderboard()
        
        # Assert: Check that the returned list matches the expected sorted order.
        self.assertEqual(leaderboard, expected_order)

    # Test the dunder methods that make the class behave like a collection.
    def test_collection_dunder_methods(self):
        '''
        Tests the __len__, __getitem__, and __iter__ dunder methods.
        '''
        # Arrange: Create a populated Scores object.
        scores = Scores([self.score_high, self.score_low])

        # Assert: Test __len__
        self.assertEqual(len(scores), 2)

        # Assert: Test __getitem__
        self.assertEqual(scores[0], self.score_high)

        # Assert: Test __iter__
        # Create a list by iterating over the Scores object.
        iterated_list = [s for s in scores]
        self.assertEqual(iterated_list, [self.score_high, self.score_low])

# This allows the test to be run from the command line.
if __name__ == '__main__':
    unittest.main()