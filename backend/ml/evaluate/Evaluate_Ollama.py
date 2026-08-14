# Importing the model
from app.models.ollama_generative import OllamaModel

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

# Required for async function
import asyncio

# Define an asynchronous main function
async def main():
    # Extracting the credentials
    load_dotenv(dotenv_path = 'credentials.env') 

    # Loading the API
    ollama_url = os.getenv('OLLAMA_API_URL')
    if not ollama_url:
        raise ValueError("OLLAMA_API_URL not found in credentials.env")

    # Instantiating the model
    model = OllamaModel(name = 'Ollama', api_url = ollama_url)

    # Path of the data
    path_data = 'evaluate/test_data.csv'

    # Loading the data
    df_data = pd.read_csv(path_data).sample(250)

    # Extracting the true value
    y_true = df_data['y'].values
    X = df_data['X'].values

    # Making predictions
    tasks = [model.predict(model.preprocess(text=x)) for x in X]
    y_pred_raw = await asyncio.gather(*tasks) # Await inside the async function

    # Convert raw float predictions to binary (0 or 1) based on your threshold
    y_pred = [1 if p > 0.5 else 0 for p in y_pred_raw]

    # Creating the figure
    fig = plt.figure(figsize = (8, 4))

    # Creating the figure
    add_evaluation(y_true = y_true, y_pred = y_pred, fig = fig, name = 'Ollama')
    fig.savefig('evaluate/Evaluate_Ollama.jpg')

# This block ensures that the main() async function is run when the script is executed
if __name__ == "__main__":
    asyncio.run(main())