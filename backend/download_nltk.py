import nltk
# Define the path relative to your project's root
# Adjust this path based on where your `nltk_data` folder actually is
nltk_data_path = './nltk_data' # Or os.path.join(os.path.dirname(__file__), 'nltk_data') if running from a script

# Create the directory if it doesn't exist
import os
os.makedirs(os.path.join(nltk_data_path, 'corpora'), exist_ok=True)
os.makedirs(os.path.join(nltk_data_path, 'tokenizers'), exist_ok=True)

# Download required packages to the specified directory
# Use quiet=True to suppress console output during download
nltk.download('wordnet', download_dir=nltk_data_path, quiet=True)
nltk.download('stopwords', download_dir=nltk_data_path, quiet=True)
nltk.download('punkt', download_dir=nltk_data_path, quiet=True) # Punkt tokenizer is often needed by lemmatizer implicitly