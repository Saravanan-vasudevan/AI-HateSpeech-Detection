# Install the project requirements before running this script.

import pandas as pd
import torch
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments

dataset = load_dataset("davidson")
df = pd.DataFrame(dataset['train'])
df = df.rename(columns={"tweet": "text", "class": "label"})
label_map = {0: "hate", 1: "offensive", 2: "safe"}
df["label_text"] = df["label"].map(label_map)
df["label_id"] = df["label_text"].map({"safe": 0, "offensive": 1, "hate": 2})
df = df.dropna()

X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label_id"], test_size=0.2, stratify=df["label_id"], random_state=42)

tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
train_encodings = tokenizer(list(X_train), truncation=True, padding=True, max_length=128)
test_encodings = tokenizer(list(X_test), truncation=True, padding=True, max_length=128)

class HateSpeechDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item
    def __len__(self):
        return len(self.labels)

train_dataset = HateSpeechDataset(train_encodings, y_train.tolist())
test_dataset = HateSpeechDataset(test_encodings, y_test.tolist())

model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=4,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=10,
    learning_rate=2e-5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

trainer.train()

output = trainer.predict(test_dataset)
preds = np.argmax(output.predictions, axis=1)

print("Classification Report:")
print(classification_report(y_test, preds, target_names=["safe", "offensive", "hate"]))
print("Accuracy Score:", accuracy_score(y_test, preds))

conf_matrix = confusion_matrix(y_test, preds)
plt.figure(figsize=(6, 5))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=["safe", "offensive", "hate"], yticklabels=["safe", "offensive", "hate"])
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

model.save_pretrained("hate_speech_model")
tokenizer.save_pretrained("hate_speech_model")

def classify_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = torch.argmax(logits).item()
    return ["safe", "offensive", "hate"][predicted_class]

example = "I hate everyone who talks like that."
print("Prediction:", classify_text(example))
