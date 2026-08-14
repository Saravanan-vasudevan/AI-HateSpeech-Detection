# Ensure the abstract model is accessible along with the abstract functionality
from app.models.base_model import BaseModel
from abc import ABC
import os

# Core functioality
# - I am going to use Hugging Face to achieve the core of what I need
from transformers import (
    pipeline, 
    AutoTokenizer, 
    AutoModelForCausalLM
)
# PyTorch - classification
import torch

class HuggingFaceGenerative(BaseModel):
    '''
    HuggingFaceGenerative class for hate speech detection.
    This class utilizes pre-trained models from Hugging Face's transformers library
    to classify hate speech and provide contextual explanations.
    '''
    def __init__(self, 
                model_name: str             = 'facebook/roberta-hate-speech-dynabench-r4-target', 
                 generative_model_name: str = 'EleutherAI/gpt-neo-125M',
                 use_local_models: bool     = True,
                 local_models_dir: str      = '../models_state'):
        '''
        Initializes the HuggingFaceGenerative model.

        Input args:
        - model_name (str)            : Name of the model to embeddings model to use
        - generative_model_name (str) : Name of the generative model to provide explanation
        - use_local_models (bool)     : Whether to use locally downloaded models
        - local_models_dir (str)      : Path to the directory containing local models

        Return:
        - None
        '''
        # Calling the super-class constructor and passing name
        super().__init__(name = f"HuggingFaceGenerative_{model_name.replace('/', '_')}")

        # Storing both the classifier and generative model
        self.classifier_model_name = model_name
        self.generative_model_name = generative_model_name
        self.use_local_models = use_local_models
        self.local_models_dir = local_models_dir

        # Storing the HuggingFace pipelines
        self.classifier_pipeline = None
        self.generative_pipeline = None

        # Sub-word tokenizer
        self.tokenizer = None

        # Calling the load model method
        self._load_models() 

    def _get_model_path(self, model_type: str) -> str:
        '''
        Returns the appropriate model path based on whether to use local models or not.
        
        Input args:
        - model_type (str) : Either 'classifier' or 'generative'
        
        Return:
        - (str) : Path to the model (local path or HuggingFace model name)
        '''
        # Check - Are we planning to use a local model
        # - Alternatively, we might be retrieving directly 
        #   from the HuggingFace repo
        if self.use_local_models:

            # ... Creating our path
            local_path = os.path.join(self.local_models_dir, model_type)

            # Check - Can we find the file?
            if os.path.exists(local_path):
                print(f"Using local {model_type} model from: {local_path}")
                return local_path
            
            # Catch - File cannot be foun
            else:
                print(f"Local {model_type} model not found at {local_path}, falling back to HuggingFace Hub")
                return self.classifier_model_name if model_type == 'classifier' else self.generative_model_name
        else:
            return self.classifier_model_name if model_type == 'classifier' else self.generative_model_name

    def _load_models(self):
        '''
        Internal method to load the classification and generative models.

        Input args:
        - None

        Return - None
        '''
        # Get the appropriate model paths
        classifier_path = self._get_model_path('classifier')
        generative_path = self._get_model_path('generative')

        # Establishing the classifier pipeline
        try:
            self.classifier_pipeline = pipeline('text-classification', 
                                              model = classifier_path, 
                                              return_all_scores = True)
            print(f"Successfully loaded classifier from: {classifier_path}")

        # Broadingly catching exceptions from looading the model
        except Exception as e:
            print(f"Error loading classifier model: {e}")
            self.classifier_pipeline = None
        
        # Attempting to load the generative model
        try:

            # Retrieving tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(generative_path)
            model = AutoModelForCausalLM.from_pretrained(generative_path) # <-- SIMPLIFIED
            
            # Check - Has padding token been specified?
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Creating pipeline to preprocess / predict
            self.generative_pipeline = pipeline(
                'text-generation',
                model     = model,
                tokenizer = self.tokenizer
            )
            print(f"Successfully loaded generative model from: {generative_path}")
        
        # Catching exception 
        # - Defaulting pipeline to none
        except Exception as e:
            print(f"Warning: Could not load generative model {generative_path} due to {e}.")
            self.generative_pipeline = None

    def preprocess(self, text: str) -> str:
        '''
        Preprocesses the input text. For Hugging Face pipelines,
        the preprocessing is largely handled internally by the pipeline.
        This method will essentially just return the text as is.

        Input args:
        - text (str) : Text that we want to make a prediction with

        Return:
        - (str) : The input text, as the pipeline handles tokenization.
        '''
        # Check - Do we actually have a string?
        if not isinstance(text, str):
            raise TypeError('Input \'text\' must be a string.')
        return text

    def predict(self, preprocessed_input: str) -> float:
        '''
        Makes a prediction on preprocessed input (text).
        Returns a probability score for hate speech.

        Input args:
        - preprocessed_input (str) : The text to classify.

        Return:
        - (float) : Probability of being hate speech (0.0 to 1.0).
        '''
        # Check - Has the pipeline actually been set?
        if self.classifier_pipeline is None:
            raise RuntimeError('Classification model not loaded.')

        # Passing text to the classifier
        results = self.classifier_pipeline(preprocessed_input)

        # Defaulting hate score to 0
        hate_score = 0.0

        # RoBERTa model returns labels 'hate' and 'nothate'.
        if results and isinstance(results[0], list): 

            # Iterating through the most likely label
            for label_info in results[0]:

                # Lowering our label
                label = label_info['label'].lower() # Use lower() for consistency
                
                # Check - Is this hate?
                #         If so, we use its score
                if label == 'hate':
                    hate_score = label_info['score']
                    break

                # Else, we need to subtract from one 
                elif label == 'nothate':
                    hate_score = 1 - label_info['score']
                    break
        
        return float(hate_score)

    def predict_text(self, preprocessed_input: str) -> str:
        '''
        Makes a prediction and provides a contextual explanation.

        Input args:
        - preprocessed_input (str) : The text to analyze.

        Return:
        - (str) : A contextual explanation about whether it is hate speech and why.
        '''
        # Extracting the hate score
        hate_score = self.predict(preprocessed_input)

        # Determining if hate has been detected using probability
        is_hate_speech = hate_score > 0.5 

        # Starting the expression
        explanation = ''

        # Check - Has the pipeline been set?
        if self.generative_pipeline:
            
            # Formatting the prompt
            prompt = (
                f"The following text has been classified as {'HATE SPEECH' if is_hate_speech else 'NOT HATE SPEECH'}. "
                f"Please provide a brief explanation for this classification.\n\n"
                f"Text: \"{preprocessed_input}\"\n\nExplanation:"
            )
            # Checking - Can we generate a response
            try:
                generated_output = self.generative_pipeline(
                    prompt,
                    max_new_tokens       = 100,
                    num_return_sequences = 1
                )
                # Check - Have we got the output
                if generated_output and 'generated_text' in generated_output[0]:
                    full_text = generated_output[0]['generated_text']
                    explanation = full_text.replace(prompt, "").strip()
            
            # Reporting the exception in the error
            except Exception as e:
                explanation = f"Error during explanation generation: {e}."
        
        # If pipeline is not loaded 
        else:
            explanation = "Generative model not loaded."

        # Creating the classification
        classification_label = "Hate Speech" if is_hate_speech else "NOT Hate Speech"
        return f"Prediction: {classification_label} (Probability: {hate_score:.4f})\nContextual Explanation: {explanation}"

    def load(self, model_path: str = None) -> None:
        '''
        Loads the models. For Hugging Face models, this is often handled
        during initialization by specifying the model_name. This method
        can be used to re-load if necessary or if models are not loaded on init.

        Input args:
        - model_path (str) : Path to model (optional - will default to HuggingFace)
        '''
        # Check - Has model path been provided?
        if model_path:
            print(f"Attempting to load classifier from local path: {model_path}")
            self.classifier_pipeline = pipeline("text-classification", model = model_path, return_all_scores = True)
        
        # Else, no path provided 
        else:
            print("No specific model path provided for loading. Re-initializing models by name.")
            self._load_models()

    def save(self, model_path: str) -> None:
        '''
        Saves the Hugging Face classification model (and potentially tokenizer)
        to the specified path. Note: Saving large generative models can be
        resource-intensive and might not always be practical if not fine-tuned.

        Input args:
        - model_path (str) : Path to the directory where the model will be saved.
        '''
        # Check - Have we got the classifier model?
        # - If so, saving them
        if self.classifier_pipeline and self.classifier_pipeline.model and self.classifier_pipeline.tokenizer:
            print(f"Saving classification model to {model_path}")
            self.classifier_pipeline.model.save_pretrained(model_path)
            self.classifier_pipeline.tokenizer.save_pretrained(model_path)
        else:
            print("Classification model not loaded, cannot save.")

        # Have we got the generative model?
        # - If so saving, them
        if self.generative_pipeline and self.generative_pipeline.model and self.generative_pipeline.tokenizer:
            gen_model_save_path = f"{model_path}_generative"
            print(f"Saving generative model to {gen_model_save_path} (caution: can be very large).")
            self.generative_pipeline.model.save_pretrained(gen_model_save_path)
            self.generative_pipeline.tokenizer.save_pretrained(gen_model_save_path)
        else:
            print("Generative model not loaded, skipping generative model save.")