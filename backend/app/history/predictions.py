import datetime
from dateutil.parser import parse as dateutil_parse
from app.history.prediction import Prediction

class Predictions:
    '''
    A class to store and manage a collection of Prediction objects.
    It provides functionality to retrieve a sorted subset of predictions.
    '''
    # Placeholder to store the list of predictions
    _predictions = None

    def __init__(self, initial_predictions: list = None) -> None:
        '''
        Initializes an empty list to store Prediction objects,
        or populates it with a given list of Prediction objects.

        Input args:
        - initial_predictions (list, optional): A list of Prediction objects

        Raises:
        - TypeError: If initial_predictions is not a list, or if any item
                     within the list is not an instance of Prediction.

        Return:
        - None
        '''
        # Setting the list of predictions to be an empty list
        self._predictions = []

        # Check - Has actual predictions been supplied? 
        if initial_predictions is not None:

            # Check - Is what is supplied actually a list?
            if not isinstance(initial_predictions, list):
                raise TypeError('Initial_predictions must be a list of Prediction objects.')
            
            # If successful, starting to add the predictions. N.B - There is validation within the 
            # method to check suitability
            for prediction in initial_predictions:
                self.add_prediction(prediction) 

    def add_prediction(self, prediction: Prediction) -> None:
        '''
        Adds a single Prediction object to the collection.

        Input args:
        - prediction (Prediction): An instance of the Prediction class.

        Raises:
        - TypeError: If the provided object is not an instance of Prediction.
        '''
        # Check - Has an actual Prediction option been supplied?
        if not isinstance(prediction, Prediction):
            raise TypeError("Only instances of 'Prediction' can be added.")
        self._predictions.append(prediction)

    def get_n_predictions(self, n: int) -> list:
        '''
        Returns the 'n' most recent predictions, sorted in descending date order.

        Input args:
        - n (int): The number of predictions to return.

        Returns:
        - list: A list of Prediction objects, sorted by date in descending order.

        Raises:
        - ValueError: If 'n' is not a positive integer.
        '''
        # Check - Has an actual positive integer been supplied?
        if not isinstance(n, int) or n <= 0:
            raise ValueError("The number of predictions 'n' must be a positive integer.")


        # Performing the reverse sort
        # We want this to be reverse by date time
        sorted_predictions = sorted(
            self._predictions,
            key     = lambda prediction: prediction.get_datetime_object(),
            reverse = True
        )
        # Return the first 'n' predictions or all available if 'n' is too large
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