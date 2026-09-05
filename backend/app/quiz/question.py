class Question:
    '''
    Multiple choice quiz question for use
    in the hate speech question
    '''
    _question = None
    _answers  = None
    _answer   = None

    def __init__(self, question : str, answers : list[str], answer : int) -> None:
        if not isinstance(question, str) or not question.strip():
            raise ValueError('Question must be a non-empty string.')

        self._question = question

        if not isinstance(answers, list) or not answers:
            raise ValueError('Answers must be a non-empty list.')
        if not all(isinstance(ans, str) and ans.strip() for ans in answers):
            raise ValueError('All answers in the list must be non-empty strings.')

        self._answers = answers

        if not isinstance(answer, int):
            raise TypeError('Answer index must be an integer.')
        if not (0 <= answer < len(self._answers)):
            raise IndexError('Answer index is out of bounds for the provided answers.')

        self._answer = answer

    def get_question(self) -> str:
        return self._question

    def get_answers(self) -> list[str]:
        return self._answers

    def get_answer(self) -> int:
        return self._answer

    def is_correct(self, answer : int) -> bool:
        if not isinstance(answer, int):
            return False

        correct = answer == self._answer

        return correct