
import datetime
from dateutil.parser import parse as dateutil_parse
import dateutil.parser
class Prediction:
    '''
    An entry that a student has made where the predicted
    if hateful or note
    '''
    # Attributes of the obect
    _username          = None     # User who made these predictions
    _datetime          = None     # Date / time that prediction was made
    _text              = None     # The text that was classified
    _human             = None     # Label from the human
    _ai                = None     # AI predictions
    _score             = None     # Score they may have got as a result
    _human_explanation = None     # Human / Students explanation of why hate speech
    _ai_explanation    = None     # Model's expalanation of why this is hate speech
    _p                 = None     # Probabiltiy of it being hate speech

    def __init__(self, username : str, datetime_str : str, text : str, human : bool, ai : bool,
                 human_explanation : str, ai_explanation : str, p : float) -> None:
        '''
        Sets up the prediction that has been made by the student

        Input args:
        - username (str)          : The username of student who made 
        - datetime_str (str)      : Representation of the data time when prediction was made
        - text (str)              : The text that was classified by the student
        - human (bool)            : The prediction that was made by the student
        - ai (bool)               : The prediction of the AI model
        - human_explanation (str) : What the student put as to why they think it is hate speech
        - ai_explanation (str)    : What the AI thinks is the reason it is hate speech
        - p (float)               : Probability of it being hate

        Return:
        - None
        '''
        # Validation
        # Check 1 - Is username actually population
        if not isinstance(username, str) or not username.strip():
            raise ValueError('Username must be a non-empty string.')

        # Check 2 - Is the date time format actually correct?
        try:
            # Using the format for '12th June 2025'
            self._datetime = dateutil_parse(datetime_str)
        except ValueError:

            # Updated error message to reflect the expected format
            raise ValueError(
                f'Datetime must be a valid, recognizable date/time string. '
                f'Received: \'{datetime_str}\''
            )

        # Check 3 - Is the text actually populated with a string?
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Text must be a non-empty string.')

        # Check 4 - Is the human prediction actually a boolean?
        if not isinstance(human, bool):
            raise TypeError('Human prediction must be a boolean.')

        # Check 5 - Is the AI prediction actually a boolean?
        if not isinstance(ai, bool):
            raise TypeError('AI prediction must be a boolean.')
        
        # Check 6 - Is the human expalantion a string
        if not isinstance(human_explanation, str):
            raise TypeError('Human explanation must be a string.')
        
        # Check 7 - Is the AI expalantion a string
        if not isinstance(ai_explanation, str):
            raise TypeError('AI explanation must be a string.')
        
        # Check - Is probability a float?
        if not isinstance(p, float):
            raise TypeError('Probability must be a float.')
        
        # Check 9 - Is probabiltiy of float in the right range?
        if not (0.0 <= p <= 1.0):
            raise ValueError('Probability must be between 0.0 and 1.0.')

        # Storing the attributes
        self._username           = username
        self._text               = text
        self._human              = human
        self._ai                 = ai
        self._score              = 10 if (self._ai == self._human) else 0
        self._human_explanation  = human_explanation
        self._ai_explanation     = ai_explanation
        self._p                  = p 

    def get(self) -> dict:
        '''
        Retrievies the entry about the
        prediction
        '''
        # Creating a dictionary of the prediction
        prediction = {
            'username'          : self._username,
            'datetime'          : self._datetime.isoformat(),
            'text'              : self._text,
            'human_prediction'  : self._human,
            'ai_prediction'     : self._ai,
            'score'             : self._score,
            'ai_explanation'    : self._ai_explanation or '',
            'human_explanation' : self._human_explanation or '',
            'probability'       : self._p

        }
        # Returning our prediction
        return prediction
    
    def get_datetime_object(self) -> datetime.datetime:
        '''
        Returns the datetime object, useful for sorting.

        Input args:
        - None

        Return:
        - (datetime.datetime) : The datetime object
        '''
        return self._datetime

