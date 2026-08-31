from app.models.base_model import BaseModel
import os
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch


class HuggingFaceGenerative(BaseModel):
    """Two-stage pipeline: a RoBERTa-based classifier for the hate/not-hate
    decision, and a small causal LM (GPT-Neo 125M by default) that writes a
    short explanation of the classification.

    Both models can be loaded from a local directory (for Docker / offline use)
    or pulled from the Hub.
    """

    def __init__(self,
                 model_name: str            = 'facebook/roberta-hate-speech-dynabench-r4-target',
                 generative_model_name: str = 'EleutherAI/gpt-neo-125M',
                 use_local_models: bool     = True,
                 local_models_dir: str      = '../models_state'):
        super().__init__(name=f"HuggingFaceGenerative_{model_name.replace('/', '_')}")
        self.classifier_model_name = model_name
        self.generative_model_name = generative_model_name
        self.use_local_models = use_local_models
        self.local_models_dir = local_models_dir

        self.classifier_pipeline = None
        self.generative_pipeline = None
        self.tokenizer = None

        self._load_models()

    # -- internal helpers --

    def _get_model_path(self, kind: str) -> str:
        """Return local path if it exists, otherwise fall back to the Hub name."""
        if self.use_local_models:
            local = os.path.join(self.local_models_dir, kind)
            weight_files = ('model.safetensors', 'pytorch_model.bin')
            if os.path.isdir(local) and any(os.path.isfile(os.path.join(local, f)) for f in weight_files):
                print(f"Using local {kind} model: {local}")
                return local
            print(f"Local {kind} not found at {local}, falling back to Hub")
        return self.classifier_model_name if kind == 'classifier' else self.generative_model_name

    def _load_models(self):
        classifier_path = self._get_model_path('classifier')
        generative_path = self._get_model_path('generative')

        try:
            self.classifier_pipeline = pipeline(
                'text-classification', model=classifier_path, return_all_scores=True)
            print(f"Classifier loaded from {classifier_path}")
        except Exception as e:
            print(f"Failed to load classifier: {e}")
            self.classifier_pipeline = None

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(generative_path)
            model = AutoModelForCausalLM.from_pretrained(generative_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.generative_pipeline = pipeline(
                'text-generation', model=model, tokenizer=self.tokenizer)
            print(f"Generative model loaded from {generative_path}")
        except Exception as e:
            print(f"Could not load generative model ({generative_path}): {e}")
            self.generative_pipeline = None

    # -- BaseModel interface --

    def preprocess(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("Expected a string")
        return text

    def predict(self, text: str) -> float:
        """Return P(hate) from the RoBERTa classifier."""
        if self.classifier_pipeline is None:
            raise RuntimeError('Classifier not loaded')

        results = self.classifier_pipeline(text)
        hate_score = 0.0
        if results and isinstance(results[0], list):
            for entry in results[0]:
                label = entry['label'].lower()
                if label == 'hate':
                    hate_score = entry['score']
                    break
                if label == 'nothate':
                    hate_score = 1.0 - entry['score']
                    break
        return float(hate_score)

    def predict_text(self, text: str) -> str:
        """Classify, then generate a short contextual explanation."""
        score = self.predict(text)
        is_hate = score > 0.5
        label = 'HATE SPEECH' if is_hate else 'NOT HATE SPEECH'

        explanation = ''
        if self.generative_pipeline:
            prompt = (
                f'The following text has been classified as {label}. '
                f'Please provide a brief explanation for this classification.\n\n'
                f'Text: "{text}"\n\nExplanation:'
            )
            try:
                out = self.generative_pipeline(prompt, max_new_tokens=100,
                                               num_return_sequences=1)
                if out and 'generated_text' in out[0]:
                    explanation = out[0]['generated_text'].replace(prompt, '').strip()
            except Exception as e:
                explanation = f"Explanation generation error: {e}"
        else:
            explanation = "Generative model not loaded."

        classification = "Hate Speech" if is_hate else "NOT Hate Speech"
        return f"Prediction: {classification} (Probability: {score:.4f})\nContextual Explanation: {explanation}"

    def load(self, model_path: str = None) -> None:
        if model_path:
            self.classifier_pipeline = pipeline(
                'text-classification', model=model_path, return_all_scores=True)
        else:
            self._load_models()

    def save(self, model_path: str) -> None:
        if self.classifier_pipeline and self.classifier_pipeline.model:
            self.classifier_pipeline.model.save_pretrained(model_path)
            self.classifier_pipeline.tokenizer.save_pretrained(model_path)
        if self.generative_pipeline and self.generative_pipeline.model:
            gen_path = f"{model_path}_generative"
            self.generative_pipeline.model.save_pretrained(gen_path)
            self.generative_pipeline.tokenizer.save_pretrained(gen_path)
