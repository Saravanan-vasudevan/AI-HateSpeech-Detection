from abc import ABC, abstractmethod

class BaseModel(ABC):
    """Common interface every prediction model must implement.

    Subclasses handle wildly different backends (sklearn, PyTorch, REST APIs)
    so the signatures are intentionally loose on input types.
    """

    def __init__(self, name: str) -> None:
        self.name  = name
        self.model = None   # populated by subclass

    @abstractmethod
    def preprocess(self, text: str):
        """Turn raw text into whatever the model's predict() expects."""
        ...

    @abstractmethod
    def predict(self, preprocessed_input) -> float:
        """Return P(hate speech) in [0, 1]."""
        ...

    @abstractmethod
    def predict_text(self, preprocessed_input) -> str:
        """Return a human-readable label / explanation string."""
        ...

    @abstractmethod
    def load(self, model_path: str) -> None:
        """Load weights / artifacts from disk.  No-op for cloud-only models."""
        ...

    @abstractmethod
    def save(self, model_path: str):
        """Persist weights / artifacts.  No-op for cloud-only models."""
        ...

    def __str__(self):
        return f"Model: {self.name}"

    def __repr__(self):
        return f"<BaseModel(name='{self.name}')>"
