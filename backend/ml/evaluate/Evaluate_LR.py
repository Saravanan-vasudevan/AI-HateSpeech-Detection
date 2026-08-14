# Importing the model
from app.models.sklearn_model import SklearnModel

# Importing matplotlib
import matplotlib.pyplot as plt

# Importing pandas and numpy
import numpy as np
import pandas as pd

# Importing method to create figure
from evaluate.evaluate_model import add_evaluation

# Path of the model file
path_model = 'models_state/LR_English_TFIDF_TM_20250629.joblib'

# Instantiating the model
model = SklearnModel()
model.load(model_path = path_model)

# Path of the data
path_data = 'evaluate/test_data.csv'

# Loading the data
df_data = pd.read_csv(path_data)

# Extracting the true value
y_true = df_data['y'].values
X      = df_data['X'].values

# Making predictions
y_pred = [1 if model.predict(text = x) > 0.5 else 0 for x in X]

# Creating the figure
fig = plt.figure(figsize = (8, 4))

# Creating the figure
add_evaluation(y_true = y_true, y_pred = y_pred, fig = fig, name = 'Logistic Regression')
fig.savefig('evaluate/Evaluate_LR.jpg')
