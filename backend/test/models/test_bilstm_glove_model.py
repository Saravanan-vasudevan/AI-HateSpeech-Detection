import unittest
from app.models.bilstm_glove_model import BiLSTMGloveModel

class TestBiLSTMGloveModel(unittest.TestCase):

    def setUp(self):
        self.model = BiLSTMGloveModel()

    def test_predict_label(self):
        result = self.model.predict_text("I hate you")
        self.assertIn(result, ["This is hate speech", "This is not hate speech"])

    def test_predict_prob(self):
        prob = self.model.predict("You are horrible")
        self.assertIsInstance(prob, float)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)

if __name__ == '__main__':
    unittest.main()
