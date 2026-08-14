import os
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    AutoModelForCausalLM,
    BitsAndBytesConfig
)
import torch

def download_and_save_hf_models(classifier_model_name: str, generative_model_name: str, 
                                save_directory: str) -> None:
    '''
    Downloads and saves Hugging Face models to a local directory.

    Input args:
    - classifier_model_name (str) : Name of the model you want from HF for classification
    - generative_model_name (str) : Name of the model you want from HF for generative / reason
    - save_directoy (str)         : Where the model should be saved
    '''
    # User message - Starting the same process
    print(f"Starting model download and save process to: {save_directory}")

    # Check - Has the directory been created?
    # - If no, let us create it
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        print(f"Created directory: {save_directory}")

    # Creating a path for classification
    classifier_path = os.path.join(save_directory, "classifier")

    # Check - Does the classifier file exists?
    # - If not, saving the model
    if not os.path.exists(classifier_path):
        os.makedirs(classifier_path)
        print(f"Downloading and saving classifier model '{classifier_model_name}' to {classifier_path}...")
        try:
            # For classification, we typically save the model and tokenizer separately
            model = AutoModelForSequenceClassification.from_pretrained(classifier_model_name)
            tokenizer = AutoTokenizer.from_pretrained(classifier_model_name)
            
            # Performing two part save (tokenizer and model)
            model.save_pretrained(classifier_path)
            tokenizer.save_pretrained(classifier_path)
            print("Classifier model and tokenizer saved.")

        # Catching errors
        except Exception as e:
            print(f"Error saving classifier model: {e}")
            print("Ensure you have accepted the terms for this model on Hugging Face Hub and are logged in (`huggingface-cli login`).")
    else:
        print(f"Classifier model already exists at {classifier_path}. Skipping download.")

    # Path for generative model
    generative_path = os.path.join(save_directory, "generative")

    # Check - Has the generative model already been saved?
    generative_path = os.path.join(save_directory, "generative")
    if not os.path.exists(generative_path):

        # ... If not, creating the path and loading model
        os.makedirs(generative_path)
        print(f"Downloading and saving generative model '{generative_model_name}' to {generative_path}...")
        try:
            # Load the model and tokenizer directly, with no quantization
            model = AutoModelForCausalLM.from_pretrained(generative_model_name)
            tokenizer = AutoTokenizer.from_pretrained(generative_model_name)
            
            # Save the model and tokenizer to the specified path
            model.save_pretrained(generative_path)
            tokenizer.save_pretrained(generative_path)
            print("Generative model and tokenizer saved.")
        
        # Reporting that download did not work 
        except Exception as e:
            print(f"Error saving generative model: {e}")
    else:
        print(f"Generative model already exists at {generative_path}. Skipping download.")

    # If we've readed the end, code run to completion
    print("\nModel download and save process complete.")

if __name__ == '__main__':


    # Model names
    CLASSIFIER_MODEL = "facebook/roberta-hate-speech-dynabench-r4-target"
    GENERATIVE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    LOCAL_MODELS_DIR = './models_state'

    # Performing the download
    download_and_save_hf_models(CLASSIFIER_MODEL, GENERATIVE_MODEL, LOCAL_MODELS_DIR)

    # Confirming the models are now downloaded
    print(f"\nModels are now available locally in '{LOCAL_MODELS_DIR}'.")
    print("You can now modify your HuggingFaceGenerative class to load from these paths.")