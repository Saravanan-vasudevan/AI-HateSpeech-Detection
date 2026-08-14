class Score:
    '''
    Represents a user's score, combining points from predictions and quizzes.
    '''
    def __init__(self, username: str, prediction_score: int, quiz_score: int) -> None:
        '''
        Initializes the Score object with validation for all inputs.

        Inputs:
        - username (str)        : The user's unique identifier.
        - prediction_score (int): The total score from prediction tasks.
        - quiz_score (int)      : The total score from quizzes.

        Raises:
            TypeError: If inputs are not of the expected type.
            ValueError: If inputs have an invalid value (e.g., empty username, negative score).

        Return:
        - None
        '''
        # Validate that the username is a non-empty string.
        if not isinstance(username, str):
            raise TypeError('Username must be a string.')
        if not username.strip():
            raise ValueError('Username cannot be empty.')
        
        # If passes test, storing the userna
        self._username = username

        # Validate that the prediction score is a non-negative number.
        if not isinstance(prediction_score, (int, float)):
            raise TypeError('Prediction score must be a number.')
        if prediction_score < 0:
            raise ValueError('Prediction score cannot be negative.')
        
        # If passes, storing the score
        self._prediction_score = prediction_score

        # Validate that the quiz score is a non-negative number.
        if not isinstance(quiz_score, (int, float)):
            raise TypeError('Quiz score must be a number.')
        if quiz_score < 0:
            raise ValueError('Quiz score cannot be negative.')
        
        # If so, storin the quiz score
        self._quiz_score = quiz_score

    @property
    def total_score(self) -> int:
        '''
        Calculates and returns the sum of prediction and quiz scores.

        Inputs:
        - None

        Returns:
        - int: The total combined score.
        '''
        # Combined property adds up both scores
        return self._prediction_score + self._quiz_score
    
    @property
    def username(self) -> str:
        '''
        Returns the user's username.

        Input args:
        - None
        
        Return:
        - (str) : User's username
        '''
        return self._username

    @property
    def prediction_score(self) -> int:
        '''
        Returns the score from predictions.

        Input args:
        - None

        Return:
        - (int) : Prediction score
        '''
        return self._prediction_score

    @property
    def quiz_score(self) -> int:
        '''
        Returns the score from quizzes.
        
        Input args:
        - None

        Return:
        - (int) : Point got during score
        '''
        # Returing the quiz score
        return self._quiz_score

    def to_dict(self) -> dict:
        '''
        Exports the score data to a dictionary.

        Inputs:
        - None

        Returns:
        - dict: A dictionary containing the username and all score components.
        '''
        # Creating the combined scores
        return {
            'username'        : self._username,
            'prediction_score': self._prediction_score,
            'quiz_score'      : self._quiz_score,
            'total_score'     : self.total_score
        }

    def __repr__(self) -> str:
        '''
        Returns a developer-friendly string representation of the Score object.

        Inputs:
        - None

        Return:
        - str: Representation of contents of object
        '''
        # Creating the string
        return (f"Score(username='{self._username}', "
                f"prediction_score={self._prediction_score}, "
                f"quiz_score={self._quiz_score})")