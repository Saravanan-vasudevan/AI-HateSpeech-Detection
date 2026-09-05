import nltk
nltk_data_path = './nltk_data' # Or os.path.join(os.path.dirname(__file__), 'nltk_data') if running from a script

import os
os.makedirs(os.path.join(nltk_data_path, 'corpora'), exist_ok=True)
os.makedirs(os.path.join(nltk_data_path, 'tokenizers'), exist_ok=True)

nltk.download('wordnet', download_dir=nltk_data_path, quiet=True)
nltk.download('stopwords', download_dir=nltk_data_path, quiet=True)
nltk.download('punkt', download_dir=nltk_data_path, quiet=True) # Punkt tokenizer is often needed by lemmatizer implicitly