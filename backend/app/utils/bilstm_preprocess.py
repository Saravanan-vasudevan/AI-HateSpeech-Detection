import re
import numpy as np
import torch
from collections import Counter

# Clean text: lowercase, remove non-letters, tokenize
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z']", " ", text)  # keep letters and apostrophes
    words = text.split()
    words = [w for w in words if len(w) > 1]  # remove single-letter words
    return words

# Build vocab from list of texts
def build_vocab(texts, min_freq=2):
    counter = Counter()
    for line in texts:
        tokens = clean_text(line)
        counter.update(tokens)
    vocab = {'<PAD>': 0, '<UNK>': 1}
    for word, freq in counter.items():
        if freq >= min_freq:
            vocab[word] = len(vocab)
    return vocab

# Convert a single text into list of vocab indices
def encode_text(text, vocab):
    tokens = clean_text(text)
    return [vocab.get(token, vocab['<UNK>']) for token in tokens]

# Load GloVe embeddings and match with your vocab
def load_glove_embeddings(glove_path, vocab, embedding_dim=100):
    embeddings = np.random.uniform(-0.25, 0.25, (len(vocab), embedding_dim))  # random init
    with open(glove_path, 'r', encoding='utf8') as f:
        for line in f:
            values = line.strip().split()
            word = values[0]
            if word in vocab:
                vector = np.asarray(values[1:], dtype='float32')
                embeddings[vocab[word]] = vector
    return torch.tensor(embeddings, dtype=torch.float32)
