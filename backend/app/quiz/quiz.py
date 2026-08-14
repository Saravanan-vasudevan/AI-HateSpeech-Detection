from app.quiz.question import Question

class Quiz:
    '''
    Ability to run a quiz that 
    is multiple choice
    '''
    # Object attributes
    _score     = 0    # Correct points during quiz
    _question  = None # Question that's currently be asked
    _index     = 0    # Index of current question
    _questions = None # List of questions to be asked

    def __init__(self, questions : list[Question]) -> None:
        '''
        Sets up the multiple choice
        quiz

        Input args:
        -questions (list[Questions]) : Questions to be asked (with email)

        Return:
        - None
        '''
        # Check 1 - Has a list of questions been provided?
        if not isinstance(questions, list):
            raise TypeError('Questions must be a list.')
        
        # Check 2 - Empty list of questions
        if not questions:
            raise ValueError('Questions list cannot be empty.')
        
        # Check 3 - List contains a set of questions
        if not all(isinstance(q, Question) for q in questions):
            raise TypeError('All items in the questions list must be Question objects.')
        
        # Storing the questions
        self._questions = questions
    
    def has_question(self) -> bool:
        '''
        Identifies if there is another question

        Input args:
        - None

        Return:
        - (bool) : Whether there are further
        '''
        # Checking if we have reached bounds of question
        end_list = self._index < len(self._questions)
        return end_list

    def get_question(self) -> tuple:
        '''
        Retrieves the current question in the quiz

        Input args:
        - None

        Return:
        - str  : Question to ask
        - list : List of the options
        '''
        # Checking if we've run out of questions
        if not self.has_question():
            raise IndexError('No more questions available in the quiz.')
        
        # Storing the exact question
        self._question = self._questions[self._index]

        # Incrementing the counter
        self._index += 1

        # Retrieving question and answers
        return self._question.get_question(), self._question.get_answers()
    
    def get_score(self) -> int:
        '''
        Retrieves the current score of the quiz

        Input args:
        - None

        Return:
        - (int) : Score achieved in the quizk
        '''
        return self._score

    def check_answer(self, answer : int) -> bool:
        '''
        Checks the answer to the question

        Input args:
        - answer (int) : Option that has been selected

        Return:
        - (bool) : True if user is correct
        '''
        # Check 1 - Has a question actually been retrieved?
        if self._question is None:
            raise RuntimeError('No question has been retrieved yet to check an answer against.')
        
        # Basic type checking for the input 'answer' for robustness
        # Although Question.is_correct handles non-int,
        # it's good to be explicit here if you expect an int.
        if not isinstance(answer, int):
            raise TypeError('Answer must be an integer representing the option index.')
        
        # Checking if correct
        correct = self._question.is_correct(answer)

        # If correct, incrementing the score
        if correct:
            self._score += 1

        # Returning if correct
        return correct
    
       
