import torch
import torch.nn.functional as F
import os
import pickle
import logging

from .base_model import BaseModel
from .bilstm_classifier import BiLSTMClassifier
from app.utils.bilstm_preprocess import encode_text, load_glove_embeddings

# === Setup logger ===
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BiLSTMGloveModel(BaseModel):
    '''
    BiLSTM + GloVe wrapper compatible with BaseModel for hate speech detection.
    '''

    def __init__(self,
                 name: str = 'BiLSTMGloveModel',
                 vocab_path: str = 'backend/models_state/vocab.pkl',
                 glove_path: str = 'backend/data/glove.6B.300d.txt',
                 model_path: str = 'backend/models_state/bilstm_glove.pt',
                 embedding_dim: int = 300,
                 hidden_dim: int = 128):
        '''
        Initializes the BiLSTM + GloVe model for hate speech detection.
        '''
        super().__init__(name)

        # === Load vocab
        if not os.path.exists(vocab_path):
            logger.error(f"[ERROR] Vocab file not found at {vocab_path}")
            raise FileNotFoundError(f"Vocab file not found at {vocab_path}")
        with open(vocab_path, 'rb') as f:
            self.vocab = pickle.load(f)
        logger.info(f"[INFO] Vocab loaded from {vocab_path}")

        # === Load GloVe embeddings
        if not os.path.exists(glove_path):
            logger.error(f"[ERROR] GloVe embeddings file not found at {glove_path}")
            raise FileNotFoundError(f"GloVe embeddings file not found at {glove_path}")
        embeddings = load_glove_embeddings(glove_path, self.vocab, embedding_dim)
        logger.info(f"[INFO] GloVe embeddings loaded from {glove_path}")

        # === Instantiate model
        self.model = BiLSTMClassifier(
            vocab_size=len(self.vocab),
            embedding_dim=embedding_dim,
            hidden_dim=hidden_dim,
            embeddings=embeddings
        )

        # === Load trained weights
        self.load(model_path)

    def preprocess(self, text: str):
        '''
        Converts raw text into input tensor and length tensor.
        '''
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")
        tokens = encode_text(text, self.vocab)
        length = len(tokens)
        return torch.tensor(tokens).unsqueeze(0), torch.tensor([length])

    def predict(self, text: str) -> float:
        '''
        Returns hate speech probability from 0.0 to 1.0
        '''
        self.model.eval()
        with torch.no_grad():
            x, lengths = self.preprocess(text)
            logits = self.model(x, lengths)
            prob = torch.sigmoid(logits)
        return prob.item()

    def predict_text(self, text: str) -> str:
        '''
        Returns a human-readable label: hate or not.
        '''
        prob = self.predict(text)
        return "This is hate speech" if prob >= 0.5 else "This is not hate speech"

    def save(self, model_path: str) -> None:
        '''
        Saves model weights to disk.
        '''
        torch.save(self.model.state_dict(), model_path)
        logger.info(f"[INFO] Model saved to {model_path}")

    def load(self, model_path: str) -> None:
        '''
        Loads model weights from disk.
        '''
        if not os.path.exists(model_path):
            logger.error(f"[ERROR] Model file not found at {model_path}")
            raise FileNotFoundError(f"Model file not found at {model_path}")
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()
        logger.info(f"[INFO] Model loaded from {model_path}")
