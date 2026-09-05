from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import logging
import numpy as np
import sys, os

from .base_model import BaseModel
from app.utils.nlp import preprocess_for_basic_nlp

logger = logging.getLogger(__name__)

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.append(_parent)


class SklearnModel(BaseModel):
    """TF-IDF + Logistic Regression classifier.

    The vectorizer and model are saved/loaded together as a single joblib
    artifact so there's no risk of a vocab mismatch.
    """

    def __init__(self, name: str = 'SklearnHateSpeechModel') -> None:
        super().__init__(name)
        self.vectorizer = TfidfVectorizer()
        self.model      = LogisticRegression()

    def preprocess(self, text: str) -> np.ndarray:
        """Clean + TF-IDF transform a single string."""
        cleaned = preprocess_for_basic_nlp(text=text)
        logger.debug("Preprocessed text: %s", cleaned)
        return self.vectorizer.transform([cleaned])

    def predict(self, text: str) -> float:
        """P(hate) for one piece of text."""
        features = self.preprocess(text)
        proba = self.model.predict_proba(features)[0, 1]
        logger.debug("Hate-speech probability: %s", proba)
        return proba

    def predict_text(self, text: str) -> str:
        p = self.predict(text)
        label = 'This is hate speech' if p >= 0.5 else 'This is not hate speech'
        logger.debug("Predicted label: %s", label)
        return label

    def load(self, model_path: str) -> None:
        """Load a joblib bundle containing both the LR model and the fitted vectorizer."""
        logger.debug("Loading model from %s", model_path)
        bundle = joblib.load(model_path)
        self.model      = bundle['model']
        self.vectorizer = bundle['vectorizer']
        logger.debug("Model and vectorizer loaded")

    def save(self, model_path: str) -> None:
        joblib.dump({'model': self.model, 'vectorizer': self.vectorizer}, model_path)


    def predict_batch(self, texts: list) -> list:
        """Predict class labels (0/1) for a list of texts at once."""
        processed = [preprocess_for_basic_nlp(t) for t in texts]
        features  = self.vectorizer.transform(processed)
        preds     = self.model.predict(features)
        logger.debug("Batch prediction shape: %s", preds.shape)
        return preds
