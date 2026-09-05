class Score:
    '''
    Represents a user's score, combining points from predictions and quizzes.
    '''
    def __init__(self, username: str, prediction_score: int, quiz_score: int) -> None:
        if not isinstance(username, str):
            raise TypeError('Username must be a string.')
        if not username.strip():
            raise ValueError('Username cannot be empty.')

        self._username = username

        if not isinstance(prediction_score, (int, float)):
            raise TypeError('Prediction score must be a number.')
        if prediction_score < 0:
            raise ValueError('Prediction score cannot be negative.')

        self._prediction_score = prediction_score

        if not isinstance(quiz_score, (int, float)):
            raise TypeError('Quiz score must be a number.')
        if quiz_score < 0:
            raise ValueError('Quiz score cannot be negative.')

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
        return self._prediction_score + self._quiz_score

    @property
    def username(self) -> str:
        return self._username

    @property
    def prediction_score(self) -> int:
        return self._prediction_score

    @property
    def quiz_score(self) -> int:
        return self._quiz_score

    def to_dict(self) -> dict:
        '''
        Exports the score data to a dictionary.

        Inputs:
        - None

        Returns:
        - dict: A dictionary containing the username and all score components.
        '''
        return {
            'username'        : self._username,
            'prediction_score': self._prediction_score,
            'quiz_score'      : self._quiz_score,
            'total_score'     : self.total_score
        }

    def __repr__(self) -> str:
        return (f"Score(username='{self._username}', "
                f"prediction_score={self._prediction_score}, "
                f"quiz_score={self._quiz_score})")