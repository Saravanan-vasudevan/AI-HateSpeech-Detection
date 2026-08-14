from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import numpy as np

def evaluate_metrics(y_true, y_pred):
    # Convert to numpy arrays if they aren't already
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Apply threshold to predictions (Sigmoid output assumed)
    y_pred = (y_pred >= 0.5).astype(int)

    # Calculate metrics
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)

    return acc, f1, cm
