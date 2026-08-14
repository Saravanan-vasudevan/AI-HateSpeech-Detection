class Question:
    '''
    Multiple choice quiz question for use
    in the hate speech question
    '''
    # Properties of the class
    _question = None  # What question is being asked
    _answers  = None  # List of options for multiple choice
    _answer   = None  # Index of the question that is correct

    def __init__(self, question : str, answers : list[str], answer : int) -> None:
        '''
        Sets up a given question

        Input args:
        - question (str)      : Question to ask
        - answers (list[str]) : List of potential answers
        - answer (int)        : Index of item that is correct

        Return:
        - None
        '''
        # Checking the question prompt is a valid string 
        # (i.e. a string and has text)
        if not isinstance(question, str) or not question.strip():
            raise ValueError('Question must be a non-empty string.')
        
        # Storing question propt
        self._question = question

        # Checking the list of answers
        if not isinstance(answers, list) or not answers:
            raise ValueError('Answers must be a non-empty list.')
        if not all(isinstance(ans, str) and ans.strip() for ans in answers):
            raise ValueError('All answers in the list must be non-empty strings.')

        # Storing answers and correct answer
        self._answers = answers

        # Validating the correct answer
        if not isinstance(answer, int):
            raise TypeError('Answer index must be an integer.')
        if not (0 <= answer < len(self._answers)):
            raise IndexError('Answer index is out of bounds for the provided answers.')
        
        # Storing the correct answer
        self._answer = answer

    def get_question(self) -> str:
        '''
        Retrievies the question

        Input args:
        - None

        Return:
        - (str) : Question
        '''
        return self._question
    
    def get_answers(self) -> list[str]:
        '''
        Retrieves the potential options 

        Input args:
        - None

        Return:
        - list[str] : Potential answers to the questions
        '''
        return self._answers
    
    def get_answer(self) -> int:
        '''
        Retrieves the index of the question 
        that is correct
        
        Input args:
        - None

        Return:
        - (int) : Integer (0th indexed that is true)
        '''
        return self._answer

    def is_correct(self, answer : int) -> bool:
        '''
        Determines if the correct question
        has been selected

        Input args:
        - answer (int) : Answer selected

        Return:
        - (bool) : True if correct, false otherwise
        '''
         # Basic type checking for the input 'answer' for robustness
        if not isinstance(answer, int):
            return False
        
        # Checking if correct
        correct = answer == self._answer

        # Returning the result
        return correct