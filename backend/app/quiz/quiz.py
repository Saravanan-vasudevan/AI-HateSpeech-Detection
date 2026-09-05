from app.quiz.question import Question

class Quiz:
    '''
    Ability to run a quiz that
    is multiple choice
    '''
    _score     = 0
    _question  = None
    _index     = 0
    _questions = None

    def __init__(self, questions : list[Question]) -> None:
        if not isinstance(questions, list):
            raise TypeError('Questions must be a list.')

        if not questions:
            raise ValueError('Questions list cannot be empty.')

        if not all(isinstance(q, Question) for q in questions):
            raise TypeError('All items in the questions list must be Question objects.')

        self._questions = questions

    def has_question(self) -> bool:
        end_list = self._index < len(self._questions)
        return end_list

    def get_question(self) -> tuple:
        if not self.has_question():
            raise IndexError('No more questions available in the quiz.')

        self._question = self._questions[self._index]

        self._index += 1

        return self._question.get_question(), self._question.get_answers()

    def get_score(self) -> int:
        return self._score

    def check_answer(self, answer : int) -> bool:
        if self._question is None:
            raise RuntimeError('No question has been retrieved yet to check an answer against.')

        if not isinstance(answer, int):
            raise TypeError('Answer must be an integer representing the option index.')

        correct = self._question.is_correct(answer)

        if correct:
            self._score += 1

        return correct


