import torch
import torch.nn.functional as F
import os
import pickle
import logging

from .base_model import BaseModel
from .bilstm_classifier import BiLSTMClassifier
from app.utils.bilstm_preprocess import encode_text, load_glove_embeddings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BiLSTMGloveModel(BaseModel):
    """BiLSTM + GloVe 300d wrapper.

    Not wired into the API yet (see Future Work in the README) but the model
    trains and evaluates fine standalone.
    """

    def __init__(self,
                 name: str = 'BiLSTMGloveModel',
                 vocab_path: str = 'backend/models_state/vocab.pkl',
                 glove_path: str = 'backend/data/glove.6B.300d.txt',
                 model_path: str = 'backend/models_state/bilstm_glove.pt',
                 embedding_dim: int = 300,
                 hidden_dim: int = 128):
        super().__init__(name)

        if not os.path.exists(vocab_path):
            raise FileNotFoundError(f"Vocab file missing: {vocab_path}")
        with open(vocab_path, 'rb') as f:
            self.vocab = pickle.load(f)
        logger.info("Vocab loaded (%d tokens)", len(self.vocab))

        if not os.path.exists(glove_path):
            raise FileNotFoundError(f"GloVe file missing: {glove_path}")
        embeddings = load_glove_embeddings(glove_path, self.vocab, embedding_dim)

        self.model = BiLSTMClassifier(
            vocab_size=len(self.vocab),
            embedding_dim=embedding_dim,
            hidden_dim=hidden_dim,
            embeddings=embeddings,
        )
        self.load(model_path)

    def preprocess(self, text: str):
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        tokens = encode_text(text, self.vocab)
        return torch.tensor(tokens).unsqueeze(0), torch.tensor([len(tokens)])

    def predict(self, text: str) -> float:
        self.model.eval()
        with torch.no_grad():
            x, lengths = self.preprocess(text)
            logits = self.model(x, lengths)
            return torch.sigmoid(logits).item()

    def predict_text(self, text: str) -> str:
        prob = self.predict(text)
        return "This is hate speech" if prob >= 0.5 else "This is not hate speech"

    def save(self, model_path: str) -> None:
        torch.save(self.model.state_dict(), model_path)
        logger.info("Model saved to %s", model_path)

    def load(self, model_path: str) -> None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model weights missing: {model_path}")
        self.model.load_state_dict(
            torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()
        logger.info("Model loaded from %s", model_path)
