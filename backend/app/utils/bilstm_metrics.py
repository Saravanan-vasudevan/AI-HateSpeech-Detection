from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import numpy as np

def evaluate_metrics(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    y_pred = (y_pred >= 0.5).astype(int)

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)

    return acc, f1, cm
