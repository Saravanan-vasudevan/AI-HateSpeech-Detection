import datetime
from dateutil.parser import parse as dateutil_parse
from app.history.prediction import Prediction

class Predictions:
    '''
    A class to store and manage a collection of Prediction objects.
    It provides functionality to retrieve a sorted subset of predictions.
    '''
    _predictions = None

    def __init__(self, initial_predictions: list = None) -> None:
        self._predictions = []

        if initial_predictions is not None:

            if not isinstance(initial_predictions, list):
                raise TypeError('Initial_predictions must be a list of Prediction objects.')

            for prediction in initial_predictions:
                self.add_prediction(prediction)

    def add_prediction(self, prediction: Prediction) -> None:
        if not isinstance(prediction, Prediction):
            raise TypeError("Only instances of 'Prediction' can be added.")
        self._predictions.append(prediction)

    def get_n_predictions(self, n: int) -> list:
        if not isinstance(n, int) or n <= 0:
            raise ValueError("The number of predictions 'n' must be a positive integer.")


        sorted_predictions = sorted(
            self._predictions,
            key     = lambda prediction: prediction.get_datetime_object(),
            reverse = True
        )
        return sorted_predictions[:min(n, len(sorted_predictions))]

    def __len__(self):
        '''
        Returns the total number of predictions stored.
        '''
        return len(self._predictions)

    def __getitem__(self, index):
        '''
        Allows accessing predictions by index, e.g., predictions_obj[0].
        '''
        return self._predictions[index]