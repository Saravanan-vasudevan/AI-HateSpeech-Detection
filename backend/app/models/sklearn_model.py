# Importing sci-kit learn functionality
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Importing ability to read in model files
import joblib 

# Importing model file
from .base_model import BaseModel

# Importing pre-processing method
from app.utils.nlp import preprocess_for_basic_nlp

# Importing numpy
import numpy as np

# Importing file path functionality
import sys
import os

# Get the current directory of the sklearn_model_wrapper.py file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (which is 'root/')
# This goes up one level from 'models/'
parent_dir = os.path.dirname(current_dir)

# Add the 'root/' directory to sys.path
# This allows Python to find 'utils/'
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


class SklearnModel(BaseModel):
    '''
    Ability to interact with sci-kit
    learn models for the use of model
    prediction
    '''
    def __init__(self, name: str = 'SklearnHateSpeechModel') -> None:
        '''
        Sets up the sci-kit learn model

        Input args:
        - name (str) : Name to know the model as

        Return:
        - None
        '''
        # Calling the default constructor and storing model name
        super().__init__(name)
        
        # Vectorizer and model are separate
        # Defining standardised vectorizer and
        self.vectorizer = TfidfVectorizer()
        self.model      = LogisticRegression() 

    def preprocess(self, text: str) -> np.array:
        '''
        Passing the text to the vectorizer to the argument

        Input args:
        - text (str) : Text to process

        Return:
        - (np.array) : Matrix of output
        '''
        # Processing our text
        text_processed = preprocess_for_basic_nlp(text = text)
        print(f"[DEBUG] Preprocessed single text: {text_processed}")
        
        # Scikit-learn models often take numerical features, so we need a vectorizer
        # For prediction, we need to transform the single text input
        # Note: The vectorizer needs to be fitted on training data *before*
        #       being used for prediction. This example assumes a pre-fitted one.
        return self.vectorizer.transform([text_processed])

    def predict(self, text : str) -> float:
        '''
        Makes a prediction of the probabiltiy of 
        this speech being hate speech or not

        Input args:
         - processed_input (np.array) : Processed / tokenized input

         Return:
         - (float) : Probability of hate speech
        '''
        # Retrieving a processed version of the text
        processed_input = self.preprocess(text = text)

        # Assuming binary classification, predict_proba returns probabilities for each class
        # We want the probability of the "hate" class (assuming 1 is hate)
        proba = self.model.predict_proba(processed_input)[0, 1]
        print(f"[DEBUG] Single text prediction probability (hate): {proba}")
        return proba
    
    def predict_text(self, text : str) -> str:
        '''
        Makes a prediction of the text, 
        rather than just a probability.
        This can be used to show the text
        
        Input args:
        - text (str) : Passage of text to process

        Return:
        - (str) : Text to show in inbox
        '''
        # Retrieving the prediction probability
        p = self.predict(text = text)

        # Determining what the text should be
        text_output = 'This is hate speech' if p >= 0.5 else 'This is not hate speech'
        print(f"[DEBUG] Final text output: {text_output}")
        return text_output

    def load(self, model_path: str) -> None:
        '''
        Sets the model / vectorizer to the pre-trained version

        Input args:
        - model_path (str) : Location of the model file

        Return:
        - None
        '''
        # Opening the file with model parameters
        print(f"[DEBUG] Loading model from path: {model_path}")
        loaded_artifacts = joblib.load(model_path)

        # Setting the model parameters
        self.model      = loaded_artifacts['model']
        self.vectorizer = loaded_artifacts['vectorizer']
        print("[DEBUG] Model and vectorizer loaded successfully")

    def save(self, model_path: str) -> None:
        '''
        Saves the model using the jolib file

        Input args:
        - model_path (str) : Filename that you wish to save model as

        Return:
        - None
        '''
        # Save both the model and the vectorizer
        joblib.dump({
            'model': self.model,
            'vectorizer': self.vectorizer
        }, model_path)

    def predict_batch(self, texts: list) -> list:
        '''
        Predicts the hate speech label (0 or 1) for a list of texts.

        Args:
        - texts (list of str): List of input texts.

        Returns:
        - List[int]: List of predicted class labels (0 or 1).
        '''
        # Preprocess each text
        processed = [preprocess_for_basic_nlp(t) for t in texts]
        print(f"[DEBUG] Preprocessed batch texts: {processed}")

        # Vectorize all processed texts
        features = self.vectorizer.transform(processed)
        print(f"[DEBUG] Feature shape from vectorizer: {features.shape}")

        # Predict and return
        predictions = self.model.predict(features)
        print(f"[DEBUG] Model batch predictions: {predictions}")
        return predictions
