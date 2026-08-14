# Importing ability to create abstract method
from abc import ABC, abstractmethod

class BaseModel(ABC):
    '''
    Abstract Base Class for hate speech prediction models.
    Defines the common interface for different model types.
    '''
    def __init__(self, name: str) -> None:
        '''
        Creates the abstract model for NLP task 
        but with no practical implementation

        Input args:
        - name (str) : Name of model

        Return:
        - None
        '''
        self.name  = name # Name of the model
        self.model = None # This will hold the actual model instance (PyTorch, scikit-learn, HF)

    @abstractmethod
    def preprocess(self, text: str) -> None:
        '''
        Abstract method to preprocess raw text input into a format suitable for the model.
        This will vary significantly between model types.
        
        Input args:
        - text (str) : Text that we want to make a prediction with

        Return:
        - None
        '''
        # No actual implementation of processing
        pass

    @abstractmethod
    def predict(self, preprocessed_input) -> float:
        '''
        Abstract method to make a prediction on preprocessed input.
        Returns a probability score for hate speech (e.g., 0.0 to 1.0).

        Input args:
        - preprocessed text -  This is un-typed as might be vector, tensor etc

        Return:
        - (float) : Probability of being a hateful text
        '''
        pass

    @abstractmethod
    def predict_text(self, preprocessed_input) -> float:
        '''
        Abstract method to make a prediction on preprocessed input.
        Returns text about the prediction

        Input args:
        - preprocessed text -  This is un-typed as might be vector, tensor etc

        Return:
        - (str) - Text to go in the output
        '''

    @abstractmethod
    def load(self, model_path: str) -> None:
        '''
        Abstract method to load the model from a specified path.

        Input args:
        - model_path (str) : Path to the filename storing the model

        Return:
        - None
        '''
        pass

    @abstractmethod
    def save(self, model_path: str):
        '''
        Abstract method to save the model to a specified path.

        Input args:
        - model_path (str) : Path to the model

        Return:
        - None
        '''
        pass

    def __str__(self) -> None:
        '''
        Creates a string representation
        of the model

        Input args:
        - None

        Return:
        - (str) : String of the object
        
        '''
        return f"Model: {self.name}"

    def __repr__(self):
        '''
        Type shown for the object

        Input args:
        - None

        Return:
        - (str) : Type of object
        '''
        return f"<BaseModel(name='{self.name}')>"