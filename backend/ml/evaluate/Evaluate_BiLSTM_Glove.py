# To extract the credentials
from dotenv import load_dotenv
import os

# Importing pandas and numpy
import numpy as np
import pandas as pd

# Importing method to create figure
from evaluate.evaluate_model import add_evaluation

# Importing the model
from app.models.bilstm_glove_model import BiLSTMGloveModel

# Importing visualisation
import matplotlib
import matplotlib.pyplot as plt

# Instantiating the model
model = BiLSTMGloveModel(vocab_path = 'models_state/vocab.pkl', glove_path = 'data/glove.6B.300d.txt',
                         model_path = 'models_state/bilstm_glove.pt');

# Path of the data
path_data = 'evaluate/test_data.csv'

# Loading the data
df_data = pd.read_csv(path_data).sample(250)

# Extracting the true value
y_true = df_data['y'].values
X      = df_data['X'].values

# Making predictions
y_pred = [1 if model.predict(X) > 0.5 else 0 for x in X]

# Creating the figure
fig = plt.figure(figsize = (8, 4))

# Creating the figure
add_evaluation(y_true = y_true, y_pred = y_pred, fig = fig, name = 'Gemini')
fig.savefig('evaluate/Evaluate_Gemini.jpg')