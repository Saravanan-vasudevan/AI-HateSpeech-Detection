# Importing the model
from app.models.gemini_generative import GeminiHateSpeechModel

# Importing matplotlib
import matplotlib.pyplot as plt

# To extract the credentials
from dotenv import load_dotenv
import os

# Importing pandas and numpy
import numpy as np
import pandas as pd

# Importing method to create figure
from evaluate.evaluate_model import add_evaluation

# Extracting the credentials
load_dotenv(dotenv_path = 'credentials.env') 

# Extracting the API key
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in credentials.env")

# Creating the model
model = GeminiHateSpeechModel(name='gemini-1.5-flash', api_key=gemini_api_key)

# Path of the data
path_data = 'evaluate/test_data.csv'

# Loading the data
df_data = pd.read_csv(path_data).sample(250)

# Extracting the true value
y_true = df_data['y'].values
X      = df_data['X'].values

print(model.predict(model.preprocess(text = X[0])))

# Making predictions
y_pred = [1 if model.predict(model.preprocess(text = x)) > 0.5 else 0 for x in X]

# Creating the figure
fig = plt.figure(figsize = (8, 4))

# Creating the figure
add_evaluation(y_true = y_true, y_pred = y_pred, fig = fig, name = 'Gemini')
fig.savefig('evaluate/Evaluate_Gemini.jpg')