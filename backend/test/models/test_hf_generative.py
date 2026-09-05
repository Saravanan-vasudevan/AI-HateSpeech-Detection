import unittest
from unittest.mock import patch, MagicMock, ANY
import os
import sys

current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.abspath(os.path.join(current_file_dir, '..', '..'))
sys.path.insert(0, project_root_dir)

from app.models.hf_generative import HuggingFaceGenerative

class TestHuggingFaceGenerative(unittest.TestCase):
    def setUp(self):

        self.patcher_pipeline = patch('models.hf_generative.pipeline')
        self.mock_pipeline = self.patcher_pipeline.start()

        self.patcher_auto_tokenizer = patch('models.hf_generative.AutoTokenizer')
        self.mock_auto_tokenizer = self.patcher_auto_tokenizer.start()

        self.patcher_auto_model = patch('models.hf_generative.AutoModelForCausalLM')
        self.mock_auto_model = self.patcher_auto_model.start()

        self.patcher_os_path_exists = patch('models.hf_generative.os.path.exists')
        self.mock_os_path_exists = self.patcher_os_path_exists.start()

        self.patcher_os_path_join = patch('models.hf_generative.os.path.join', side_effect=os.path.join)
        self.mock_os_path_join = self.patcher_os_path_join.start()

        self.mock_classifier_pipeline_instance = MagicMock()
        self.mock_generative_pipeline_instance = MagicMock()
        self.mock_tokenizer_instance = MagicMock(pad_token=None, eos_token='<eos>', eos_token_id=1)
        self.mock_generative_model_instance = MagicMock()

    def tearDown(self):
        self.patcher_pipeline.stop()
        self.patcher_auto_tokenizer.stop()
        self.patcher_auto_model.stop()
        self.patcher_os_path_exists.stop()
        self.patcher_os_path_join.stop()

    def _configure_dependencies_for_load(self, classifier_exists=False, generative_exists=False):
        self.mock_os_path_exists.side_effect = lambda path: \
            ('classifier' in path and classifier_exists) or \
            ('generative' in path and generative_exists)

        self.mock_auto_tokenizer.from_pretrained.return_value = self.mock_tokenizer_instance
        self.mock_auto_model.from_pretrained.return_value = self.mock_generative_model_instance

        self.mock_pipeline.side_effect = [
            self.mock_classifier_pipeline_instance,
            self.mock_generative_pipeline_instance
        ]

    def test_init_local_models_exist(self):
        self._configure_dependencies_for_load(classifier_exists = True, generative_exists = True)

        model = HuggingFaceGenerative(use_local_models = True, local_models_dir = 'mock_dir')

        expected_generative_path = os.path.join('mock_dir', 'generative')

        self.mock_auto_model.from_pretrained.assert_called_with(expected_generative_path)

        self.mock_pipeline.assert_any_call(
            "text-generation",
            model=self.mock_generative_model_instance,
            tokenizer=self.mock_tokenizer_instance
        )

    def test_init_fallback_to_hub(self):
        self._configure_dependencies_for_load(classifier_exists = False, generative_exists = False)

        model = HuggingFaceGenerative(use_local_models = True)

        expected_model_name = 'EleutherAI/gpt-neo-125M'
        self.mock_auto_tokenizer.from_pretrained.assert_called_with(expected_model_name)

        self.mock_auto_model.from_pretrained.assert_called_with(expected_model_name)

    def test_predict_with_new_labels(self):
        self._configure_dependencies_for_load()
        model = HuggingFaceGenerative()

        model.classifier_pipeline.return_value = [[{'label': 'hate', 'score': 0.95}]]
        self.assertAlmostEqual(model.predict('I hate you'), 0.95)

        model.classifier_pipeline.return_value = [[{'label': 'nothate', 'score': 0.98}]]
        self.assertAlmostEqual(model.predict('I love you'), 1 - 0.98)

    @patch('models.hf_generative.HuggingFaceGenerative.predict')
    def test_predict_text_generates_explanation(self, mock_predict):
        self._configure_dependencies_for_load()
        model = HuggingFaceGenerative()

        mock_predict.return_value = 0.8

        model.generative_pipeline.return_value = [{'generated_text': 'A simple prompt. Explanation: a simple response.'}]

        result = model.predict_text('Some hateful text')

        model.generative_pipeline.assert_called_once()

        self.assertIn("Explanation: a simple response.", result)