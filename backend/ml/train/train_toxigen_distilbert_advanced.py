
import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments, EarlyStoppingCallback
from datasets import Dataset

# Config
CSV_PATH = "toxigen_cleaned.csv"
TAG = "toxigen"
NUM_LABELS = 3
LABEL_NAMES = ["safe", "offensive", "hate"]

# Load dataset
df = pd.read_csv(CSV_PATH)
df = df[["text", "label"]].dropna()
df["label"] = df["label"].astype(int)

# Split data
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["text"], df["label"], test_size=0.2, stratify=df["label"], random_state=42
)

# Tokenization
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
train_encodings = tokenizer(list(train_texts), truncation=True, padding=True, max_length=128)
val_encodings = tokenizer(list(val_texts), truncation=True, padding=True, max_length=128)

# Dataset formatting
train_dataset = Dataset.from_dict({**train_encodings, "label": list(train_labels)})
val_dataset = Dataset.from_dict({**val_encodings, "label": list(val_labels)})

# Model setup
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=NUM_LABELS
)

# Training args
training_args = TrainingArguments(
    output_dir=f"./results_{TAG}",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_strategy="epoch",
    load_best_model_at_end=True,
    save_total_limit=1,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=4,
    weight_decay=0.01,
    logging_dir=f"./logs_{TAG}",
    disable_tqdm=False,
    report_to="none"
)

# Compute metrics
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    report = classification_report(labels, preds, output_dict=True, zero_division=0)
    print(classification_report(labels, preds, target_names=LABEL_NAMES, zero_division=0))
    return {
        "accuracy": report["accuracy"],
        "precision": report["weighted avg"]["precision"],
        "recall": report["weighted avg"]["recall"],
        "f1": report["weighted avg"]["f1-score"]
    }

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
)

# Train and save
trainer.train()
model.save_pretrained(f"./model_{TAG}")
tokenizer.save_pretrained(f"./model_{TAG}")
