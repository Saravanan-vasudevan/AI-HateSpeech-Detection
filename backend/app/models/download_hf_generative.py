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
    print(f"Starting model download and save process to: {save_directory}")

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        print(f"Created directory: {save_directory}")

    classifier_path = os.path.join(save_directory, "classifier")

    classifier_ready = any(os.path.isfile(os.path.join(classifier_path, name))
                           for name in ("model.safetensors", "pytorch_model.bin"))
    if not classifier_ready:
        os.makedirs(classifier_path, exist_ok=True)
        print(f"Downloading and saving classifier model '{classifier_model_name}' to {classifier_path}...")
        try:
            model = AutoModelForSequenceClassification.from_pretrained(classifier_model_name)
            tokenizer = AutoTokenizer.from_pretrained(classifier_model_name)

            model.save_pretrained(classifier_path)
            tokenizer.save_pretrained(classifier_path)
            print("Classifier model and tokenizer saved.")

        except Exception as e:
            print(f"Error saving classifier model: {e}")
            print("Ensure you have accepted the terms for this model on Hugging Face Hub and are logged in (`huggingface-cli login`).")
    else:
        print(f"Classifier model already exists at {classifier_path}. Skipping download.")

    generative_path = os.path.join(save_directory, "generative")

    generative_path = os.path.join(save_directory, "generative")
    generative_ready = any(os.path.isfile(os.path.join(generative_path, name))
                           for name in ("model.safetensors", "pytorch_model.bin"))
    if not generative_ready:

        os.makedirs(generative_path, exist_ok=True)
        print(f"Downloading and saving generative model '{generative_model_name}' to {generative_path}...")
        try:
            model = AutoModelForCausalLM.from_pretrained(generative_model_name)
            tokenizer = AutoTokenizer.from_pretrained(generative_model_name)

            model.save_pretrained(generative_path)
            tokenizer.save_pretrained(generative_path)
            print("Generative model and tokenizer saved.")

        except Exception as e:
            print(f"Error saving generative model: {e}")
    else:
        print(f"Generative model already exists at {generative_path}. Skipping download.")

    print("\nModel download and save process complete.")

if __name__ == '__main__':


    CLASSIFIER_MODEL = "facebook/roberta-hate-speech-dynabench-r4-target"
    GENERATIVE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    LOCAL_MODELS_DIR = './models_state'

    download_and_save_hf_models(CLASSIFIER_MODEL, GENERATIVE_MODEL, LOCAL_MODELS_DIR)

    print(f"\nModels are now available locally in '{LOCAL_MODELS_DIR}'.")
    print("You can now modify your HuggingFaceGenerative class to load from these paths.")
