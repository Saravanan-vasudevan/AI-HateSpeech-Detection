from app.models.ollama_generative import OllamaModel

import matplotlib.pyplot as plt

from dotenv import load_dotenv
import os

import numpy as np
import pandas as pd

from evaluate.evaluate_model import add_evaluation

import asyncio

async def main():
    load_dotenv(dotenv_path = 'credentials.env')

    ollama_url = os.getenv('OLLAMA_API_URL')
    if not ollama_url:
        raise ValueError("OLLAMA_API_URL not found in credentials.env")

    model = OllamaModel(name = 'Ollama', api_url = ollama_url)

    path_data = 'evaluate/test_data.csv'

    df_data = pd.read_csv(path_data).sample(250)

    y_true = df_data['y'].values
    X = df_data['X'].values

    tasks = [model.predict(model.preprocess(text=x)) for x in X]
    y_pred_raw = await asyncio.gather(*tasks)

    y_pred = [1 if p > 0.5 else 0 for p in y_pred_raw]

    fig = plt.figure(figsize = (8, 4))

    add_evaluation(y_true = y_true, y_pred = y_pred, fig = fig, name = 'Ollama')
    fig.savefig('evaluate/Evaluate_Ollama.jpg')

if __name__ == "__main__":
    asyncio.run(main())