import unittest
from app.points.score import Score
from app.points.scores import Scores


class TestScores(unittest.TestCase):
    def setUp(self):
        self.score_low  = Score(username='user_c', prediction_score=10, quiz_score=10)
        self.score_high = Score(username='user_a', prediction_score=50, quiz_score=50)
        self.score_mid  = Score(username='user_b', prediction_score=25, quiz_score=25)

    def test_initialization(self):
        scores_empty = Scores()
        self.assertEqual(len(scores_empty), 0)

        scores_populated = Scores(initial_scores = [self.score_low, self.score_high])
        self.assertEqual(len(scores_populated), 2)
        self.assertIn(self.score_low, scores_populated)

    def test_initialization_validation(self):
        with self.assertRaisesRegex(TypeError, 'initial_scores must be a list'):
            Scores(initial_scores='not-a-list')

        with self.assertRaisesRegex(TypeError, 'Only Score objects can be added'):
            Scores(initial_scores=[self.score_low, 123, self.score_high])

    def test_add_score_method(self):
        scores = Scores()

        scores.add_score(self.score_mid)

        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0], self.score_mid)

        with self.assertRaisesRegex(TypeError, 'Only Score objects can be added'):
            scores.add_score('a-random-string')

        self.assertEqual(len(scores), 1)

    def test_get_leaderboard(self):
        scores = Scores(initial_scores=[self.score_low, self.score_high, self.score_mid])

        expected_order = [self.score_high, self.score_mid, self.score_low]

        leaderboard = scores.get_leaderboard()

        self.assertEqual(leaderboard, expected_order)

    def test_collection_dunder_methods(self):
        scores = Scores([self.score_high, self.score_low])

        self.assertEqual(len(scores), 2)

        self.assertEqual(scores[0], self.score_high)

        iterated_list = [s for s in scores]
        self.assertEqual(iterated_list, [self.score_high, self.score_low])

if __name__ == '__main__':
    unittest.main()