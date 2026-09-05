
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from torch.nn.utils.rnn import pad_sequence
import torch.nn as nn
import torch.optim as optim
import pickle
import os

from backend.models.bilstm_classifier import BiLSTMClassifier
from backend.utils.bilstm_preprocess import clean_text, build_vocab, encode_text, load_glove_embeddings
from backend.utils.bilstm_metrics import evaluate_metrics
from sklearn.model_selection import train_test_split

DATA_PATH = "backend/data/bilstm_data.csv"
GLOVE_PATH = "backend/data/glove.6B.300d.txt"
VOCAB_SAVE_PATH = "backend/models_state/vocab.pkl"
MODEL_SAVE_PATH = "backend/models_state/bilstm_glove.pt"
EMBEDDING_DIM = 300
HIDDEN_DIM = 128
BATCH_SIZE = 16
EPOCHS = 6
LEARNING_RATE = 1e-3

df = pd.read_csv(DATA_PATH)
train_df, val_df = train_test_split(df, test_size=0.15, stratify=df['label'], random_state=42)

texts = df['tweet'].astype(str).tolist()
labels = df['label'].tolist()
vocab = build_vocab(texts)
with open(VOCAB_SAVE_PATH, "wb") as f:
    pickle.dump(vocab, f)
print(f"[INFO] Vocab saved to {VOCAB_SAVE_PATH}")

encoded_texts = [torch.tensor(encode_text(text, vocab)) for text in texts]
padded_texts = pad_sequence(encoded_texts, batch_first=True)
lengths = torch.tensor([len(seq) for seq in encoded_texts])
labels = torch.tensor(labels, dtype=torch.float32)

class HateDataset(Dataset):
    def __init__(self, x, y, l):
        self.x = x
        self.y = y
        self.l = l
    def __len__(self): return len(self.y)
    def __getitem__(self, i): return self.x[i], self.y[i], self.l[i]

train_enc = [encode_text(text, vocab) for text in train_df['tweet']]
train_tensors = [torch.tensor(seq) for seq in train_enc]
train_pad = pad_sequence(train_tensors, batch_first=True)
train_len = torch.tensor([len(seq) for seq in train_tensors])
train_labels = torch.tensor(train_df['label'].tolist(), dtype=torch.float32)

val_enc = [encode_text(text, vocab) for text in val_df['tweet']]
val_tensors = [torch.tensor(seq) for seq in val_enc]
val_pad = pad_sequence(val_tensors, batch_first=True)
val_len = torch.tensor([len(seq) for seq in val_tensors])
val_labels = torch.tensor(val_df['label'].tolist(), dtype=torch.float32)

train_set = HateDataset(train_pad, train_labels, train_len)
val_set = HateDataset(val_pad, val_labels, val_len)

train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_set, batch_size=BATCH_SIZE)

embeddings = load_glove_embeddings(GLOVE_PATH, vocab, EMBEDDING_DIM)
model = BiLSTMClassifier(
    vocab_size=len(vocab),
    embedding_dim=EMBEDDING_DIM,
    hidden_dim=HIDDEN_DIM,
    embeddings=embeddings
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

loss_fn = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

best_val_f1 = 0
early_stop_counter = 0
for epoch in range(EPOCHS):
    model.train()
    for x, y, l in train_loader:
        x, y, l = x.to(device), y.to(device), l.to(device)
        optimizer.zero_grad()
        outputs = model(x, l)
        loss = loss_fn(outputs, y)
        loss.backward()
        optimizer.step()

    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for x, y, l in val_loader:
            x, y, l = x.to(device), y.to(device), l.to(device)
            logits = model(x, l)
            probs = torch.sigmoid(logits)
            all_preds.extend(probs.cpu().tolist())
            all_labels.extend(y.cpu().tolist())

    acc, f1, cm = evaluate_metrics(all_labels, all_preds)
    print(f"Epoch {epoch+1}: Val Acc={acc:.4f}, F1={f1:.4f}")

    if f1 > best_val_f1:
        best_val_f1 = f1
        early_stop_counter = 0
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        print(f"[INFO] New best model saved at epoch {epoch+1}")
    else:
        early_stop_counter += 1
        if early_stop_counter >= 2:
            print("[INFO] Early stopping triggered.")
            break

print(f"[DONE] Training complete. Best F1: {best_val_f1:.4f}")
