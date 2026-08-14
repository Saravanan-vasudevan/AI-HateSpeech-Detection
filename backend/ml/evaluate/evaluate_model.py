# Importing sci-kit learn metrics
import matplotlib.figure
from sklearn.metrics import confusion_matrix, f1_score
import seaborn as sns

# Visualisation libraries
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib

# Using numpy for results
import numpy as np
import pandas as pd

def add_evaluation(y_true : np.array, y_pred : np.array, fig : matplotlib.figure.Figure,
                   name : str) -> None:
    '''
    Creates an analysis of the different models

    Input args:
    - y_true (np.array) : True y predictions
    - y_pred (np.array) : Predicted y value
    - figure (Figure)   : Figure to store the results

    Return:
    - None
    '''
    # Calculating the 3 F1 scores
    f1_hate     = f1_score(y_true = y_true, y_pred = y_pred, pos_label = 1)
    f1_non_hate = f1_score(y_true = y_true, y_pred = y_pred, pos_label = 0)
    f1_avg      = f1_score(y_true = y_true, y_pred = y_pred, average = 'macro')

    # Calculating the confusion matrix
    cm = confusion_matrix(y_true = y_true, y_pred = y_pred)

    # Converting the confusion matrix into a dataframe
    class_labels = ['Not hate', 'Hate']
    cm_df = pd.DataFrame(cm, index = class_labels, columns = class_labels)

    # Normalising the df
    cm_normalized_row = cm_df.div(cm_df.sum(axis=1), axis=0)

    # Adding the 2 subplots
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    #################################################
    #           Plot 1 - Confusion matrix           #
    #################################################

    # Define colorbar keyword arguments for percentage formatting
    cbar_kws = {
        'format': mticker.PercentFormatter(xmax = 1.0, decimals = 0) 
    }

    sns.heatmap(
        data       = cm_normalized_row,
        cmap       = 'coolwarm',
        annot      = True,
        fmt        = '.1%',
        linewidths = .5,  
        cbar       = True,
        cbar_kws   = cbar_kws,
        ax         = ax1
    )
    ax1.set_title('Predictions')

    #################################################
    #             Plot 2 - F1 Scores Table          #
    #################################################
    
    # Prepare data for the table
    f1_scores_data = {
        'Metric': ['F1 Score (Not Hate)', 'F1 Score (Hate)', 'F1 Score (Weighted Avg)'],
        'Score': [f1_non_hate, f1_hate, f1_avg]
    }
    f1_df = pd.DataFrame(f1_scores_data)

    # Convert scores to formatted strings for display in table
    f1_df['Score'] = f1_df['Score'].apply(lambda x: f'{x:.3f}')

    # Hide the axes for the table plot
    ax2.axis('off') # Hides the x and y axis lines and ticks
    ax2.set_title('F1 Scores')

    # Create the table
    table = ax2.table(
        cellText  = f1_df.values,
        colLabels = f1_df.columns,
        cellLoc   = 'center',
        loc       = 'center')

    # Adjust table properties for better appearance
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2) # Scale the table size (width, height)

    # Adding a title
    fig.suptitle('Model: %s' % name)

    # Adjust layout to prevent overlapping titles/labels
    fig.tight_layout()

