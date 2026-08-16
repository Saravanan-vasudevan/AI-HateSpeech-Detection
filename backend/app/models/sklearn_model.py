from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import numpy as np
import sys, os

from .base_model import BaseModel
from app.utils.nlp import preprocess_for_basic_nlp

# Make sure the parent dir is importable (needed when running outside the
# normal package layout, e.g. from a notebook).
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
        print(f"[DEBUG] Preprocessed: {cleaned}")
        return self.vectorizer.transform([cleaned])

    def predict(self, text: str) -> float:
        """P(hate) for one piece of text."""
        features = self.preprocess(text)
        proba = self.model.predict_proba(features)[0, 1]
        print(f"[DEBUG] P(hate) = {proba}")
        return proba

    def predict_text(self, text: str) -> str:
        p = self.predict(text)
        label = 'This is hate speech' if p >= 0.5 else 'This is not hate speech'
        print(f"[DEBUG] Label: {label}")
        return label

    def load(self, model_path: str) -> None:
        """Load a joblib bundle containing both the LR model and the fitted vectorizer."""
        print(f"[DEBUG] Loading model from {model_path}")
        bundle = joblib.load(model_path)
        self.model      = bundle['model']
        self.vectorizer = bundle['vectorizer']
        print("[DEBUG] Model + vectorizer loaded")

    def save(self, model_path: str) -> None:
        joblib.dump({'model': self.model, 'vectorizer': self.vectorizer}, model_path)

    # --- Batch helpers (used by evaluation scripts) ---

    def predict_batch(self, texts: list) -> list:
        """Predict class labels (0/1) for a list of texts at once."""
        processed = [preprocess_for_basic_nlp(t) for t in texts]
        features  = self.vectorizer.transform(processed)
        preds     = self.model.predict(features)
        print(f"[DEBUG] Batch predictions shape: {preds.shape}")
        return preds
