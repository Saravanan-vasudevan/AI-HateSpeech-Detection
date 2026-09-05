import re
import numpy as np
import torch
from collections import Counter

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z']", " ", text)
    words = text.split()
    words = [w for w in words if len(w) > 1]
    return words

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

def encode_text(text, vocab):
    tokens = clean_text(text)
    return [vocab.get(token, vocab['<UNK>']) for token in tokens]

def load_glove_embeddings(glove_path, vocab, embedding_dim=100):
    embeddings = np.random.uniform(-0.25, 0.25, (len(vocab), embedding_dim))
    with open(glove_path, 'r', encoding='utf8') as f:
        for line in f:
            values = line.strip().split()
            word = values[0]
            if word in vocab:
                vector = np.asarray(values[1:], dtype='float32')
                embeddings[vocab[word]] = vector
    return torch.tensor(embeddings, dtype=torch.float32)
