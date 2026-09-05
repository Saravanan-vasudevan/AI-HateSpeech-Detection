from dotenv import load_dotenv
import os

import numpy as np
import pandas as pd

from evaluate.evaluate_model import add_evaluation

from app.models.bilstm_glove_model import BiLSTMGloveModel

import matplotlib
import matplotlib.pyplot as plt

model = BiLSTMGloveModel(vocab_path = 'models_state/vocab.pkl', glove_path = 'data/glove.6B.300d.txt',
                         model_path = 'models_state/bilstm_glove.pt');

path_data = 'evaluate/test_data.csv'

df_data = pd.read_csv(path_data).sample(250)

y_true = df_data['y'].values
X      = df_data['X'].values

y_pred = [1 if model.predict(X) > 0.5 else 0 for x in X]

fig = plt.figure(figsize = (8, 4))

add_evaluation(y_true = y_true, y_pred = y_pred, fig = fig, name = 'Gemini')
fig.savefig('evaluate/Evaluate_Gemini.jpg')