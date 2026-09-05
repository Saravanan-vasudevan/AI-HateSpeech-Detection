
import datetime
from dateutil.parser import parse as dateutil_parse
import dateutil.parser
class Prediction:
    '''
    An entry that a student has made where the predicted
    if hateful or note
    '''
    _username          = None
    _datetime          = None
    _text              = None
    _human             = None
    _ai                = None
    _score             = None
    _human_explanation = None
    _ai_explanation    = None
    _p                 = None

    def __init__(self, username : str, datetime_str : str, text : str, human : bool, ai : bool,
                 human_explanation : str, ai_explanation : str, p : float) -> None:
        if not isinstance(username, str) or not username.strip():
            raise ValueError('Username must be a non-empty string.')

        try:
            self._datetime = dateutil_parse(datetime_str)
        except ValueError:

            raise ValueError(
                f'Datetime must be a valid, recognizable date/time string. '
                f'Received: \'{datetime_str}\''
            )

        if not isinstance(text, str) or not text.strip():
            raise ValueError('Text must be a non-empty string.')

        if not isinstance(human, bool):
            raise TypeError('Human prediction must be a boolean.')

        if not isinstance(ai, bool):
            raise TypeError('AI prediction must be a boolean.')

        if not isinstance(human_explanation, str):
            raise TypeError('Human explanation must be a string.')

        if not isinstance(ai_explanation, str):
            raise TypeError('AI explanation must be a string.')

        if not isinstance(p, float):
            raise TypeError('Probability must be a float.')

        if not (0.0 <= p <= 1.0):
            raise ValueError('Probability must be between 0.0 and 1.0.')

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
        return prediction

    def get_datetime_object(self) -> datetime.datetime:
        return self._datetime

