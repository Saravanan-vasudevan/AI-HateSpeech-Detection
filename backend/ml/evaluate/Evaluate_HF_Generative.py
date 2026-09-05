from app.models.hf_generative import HuggingFaceGenerative

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

from evaluate.evaluate_model import add_evaluation

path_model = '/models_state'

model = HuggingFaceGenerative(use_local_models = True, local_models_dir = path_model)

path_data = 'evaluate/test_data.csv'

df_data = pd.read_csv(path_data)

y_true = df_data['y'].values
X      = df_data['X'].values

y_pred = [1 if model.predict(model.preprocess(text = x)) > 0.5 else 0 for x in X]

fig = plt.figure(figsize = (8, 4))

add_evaluation(y_true = y_true, y_pred = y_pred, fig = fig, name = 'HF - Generative')
fig.savefig('evaluate/Evaluate_HF_Generative.jpg')