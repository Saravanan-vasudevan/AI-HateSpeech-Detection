import matplotlib.figure
from sklearn.metrics import confusion_matrix, f1_score
import seaborn as sns

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib

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
    f1_hate     = f1_score(y_true = y_true, y_pred = y_pred, pos_label = 1)
    f1_non_hate = f1_score(y_true = y_true, y_pred = y_pred, pos_label = 0)
    f1_avg      = f1_score(y_true = y_true, y_pred = y_pred, average = 'macro')

    cm = confusion_matrix(y_true = y_true, y_pred = y_pred)

    class_labels = ['Not hate', 'Hate']
    cm_df = pd.DataFrame(cm, index = class_labels, columns = class_labels)

    cm_normalized_row = cm_df.div(cm_df.sum(axis=1), axis=0)

    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)


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


    f1_scores_data = {
        'Metric': ['F1 Score (Not Hate)', 'F1 Score (Hate)', 'F1 Score (Weighted Avg)'],
        'Score': [f1_non_hate, f1_hate, f1_avg]
    }
    f1_df = pd.DataFrame(f1_scores_data)

    f1_df['Score'] = f1_df['Score'].apply(lambda x: f'{x:.3f}')

    ax2.axis('off')
    ax2.set_title('F1 Scores')

    table = ax2.table(
        cellText  = f1_df.values,
        colLabels = f1_df.columns,
        cellLoc   = 'center',
        loc       = 'center')

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    fig.suptitle('Model: %s' % name)

    fig.tight_layout()

