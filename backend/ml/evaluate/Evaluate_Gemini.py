from app.models.gemini_generative import GeminiHateSpeechModel

import matplotlib.pyplot as plt

from dotenv import load_dotenv
import os

import numpy as np
import pandas as pd

from evaluate.evaluate_model import add_evaluation

load_dotenv(dotenv_path = 'credentials.env')

gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in credentials.env")

model = GeminiHateSpeechModel(name='gemini-1.5-flash', api_key=gemini_api_key)

path_data = 'evaluate/test_data.csv'

df_data = pd.read_csv(path_data).sample(250)

y_true = df_data['y'].values
X      = df_data['X'].values

print(model.predict(model.preprocess(text = X[0])))

y_pred = [1 if model.predict(model.preprocess(text = x)) > 0.5 else 0 for x in X]

fig = plt.figure(figsize = (8, 4))

add_evaluation(y_true = y_true, y_pred = y_pred, fig = fig, name = 'Gemini')
fig.savefig('evaluate/Evaluate_Gemini.jpg')