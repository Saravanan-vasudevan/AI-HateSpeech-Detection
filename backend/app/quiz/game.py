from app.utils.database import Database
from app.quiz.question import Question
from app.quiz.quiz import Quiz
import numpy as np

class Game:
    '''
    Application layer that loads the 
    quiz 
    '''
    # Set properties of the class
    _db         = None    # Database connection
    _collection = None    # Name of the collection
    _hardness   = None    # Specified hardness of the quiz
    _questions  = None    # Number of questions

    # Quiz itself
    _quiz = None   # Playing the quiz itself

    # Username 
    _username = None

    # Where collection is write
    _col_write = 'quiz_scores'


    def __init__(self, db : Database, collection : str, hardness : int,
                 questions : int, username : str) -> None:
        '''
        Sets up the quiz by extracting n random samples
        from the database

        Input args:
        - db (Database)   : Connection to the database
        - collection (str): Name of the collection
        - hardness (int)  : Specifies how hard the quiz should be (0, 1, 2)
        - questions (int) : Number of questions that you want in the quiz

        Return:
        - None
        '''
        # Performing validation on the input arguments
        self._validate_db(db = db)
        self._validate_hardness(hardness = hardness)
        self._validate_questions(questions = questions)

        # Storing the attributes
        self._db         = db
        self._collection = collection
        self._questions  = questions
        self._hardness   = hardness
        self._username   = username

        # Call the setup
        self._setup()
    

    def _validate_db(self, db: Database) -> None:
        '''
        Validates that 'db' is an instance of the Database class.
        Raises a TypeError if the validation fails.
        
        Input args:
        - db (Database) : Connection to the database object

        Return:
        - None
        '''
        # Check 1 - Is this the database?
        if not isinstance(db, Database):
            raise TypeError('The db argument must be an instance of the Database class.')

    def _validate_hardness(self, hardness: int) -> None:
        '''
        Validates that 'hardness' is an integer and takes values 0, 1, or 2.
        Raises a TypeError if not an integer, or a ValueError if outside the allowed range.
        
        Input args:
        - hardness (int) : Perceived hardness of the quiz

        Return:
        - None
        '''
        # Check 1 - Is this an integer?
        if not isinstance(hardness, int):
            raise TypeError('The hardness argument must be an integer.')
        
        # Check 2 - Is hardness taking a valid integer?
        if hardness not in [0, 1, 2]:
            raise ValueError('The hardness argument must be 0, 1, or 2.')

    def _validate_questions(self, questions: int) -> None:
        '''
        Validates that 'questions' is a positive integer.
        Raises a TypeError if not an integer, or a ValueError if not positive.
        
        Input args:
        - questions (int) : Number of questions for the quiz
        '''
        # Check 1 - Is the hardness argument an integer?
        if not isinstance(questions, int):
            raise TypeError('The questions argument must be an integer.')
        
        # Check 2 - Is the # Number of question actually valid?
        if questions < 1:
            raise ValueError('The questions argument must be a positive integer.')
        
    def _validate_username(self, username: str) -> None:
        '''
        Ensures that the username is in a correct format itself

        Input args:
        - username (str) : Candidate username

        Return:
        - None
        '''
        # Check 1 - has the username passed actually a string?
        if not isinstance(username, str):
            raise TypeError('The username argument must be a string.')
        
        # Check 2 - Is there actually characters in this string?
        if not username.strip(): 
            raise ValueError('The username argument cannot be empty or just whitespace.')
        
    def _setup(self) -> None:
        '''
        Populates the quiz object ready for use

        Input args:
        - None

        Return:
        - None
        '''
        # Populating the query
        query_hardness = {'level' : self._hardness}

        # Retrieving the dictionary
        questions_list = self._db.get_records(collection_name = self._collection,
                                              query = query_hardness)

        # Check - No question returned
        if len(questions_list) == 0:
            raise ValueError('Failed to retrieve any questions of the appropriate hardness')

        # Determining number of questions to populate
        # Ideally, this should be the total number of questions
        # but it can be the the maximum question
        n_selected = self._questions if len(questions_list) > self._questions else len(questions_list)

        # Specify the questions
        n_available = np.arange(start = 0, stop = len(questions_list))

        # Determining which questions to ask
        index_selected = np.random.choice(n_available, n_selected, replace = False)

        # Creating our list of questions
        question_list = []
        for i in index_selected:

            # Extracting the dictionary
            q = questions_list[i]

            # Creatin the question object
            question = Question(question = q['question'], answers = [q['A'], q['B'], q['C'], q['D']],
                                answer = q['answer'])
            question_list.append(question)
        
        # Creating the quiz itself
        self._quiz = Quiz(questions = question_list)

    def get_question(self) -> tuple:
        '''
        Retrieves the current question and its options from the quiz.

        Input args:
        - None

        Return:
        - tuple : A tuple containing the question string and a list of answer options.
        '''
        # Checking the quick has been populated
        if self._quiz is None:
            raise RuntimeError('Quiz has not been initialized. Call _setup() first.')
        
        # Else, retrieving the question
        return self._quiz.get_question()
    
    def check_answer(self, answer: int) -> bool:
        '''
        Checks if the provided answer is correct for the current question.
        Updates the quiz score if the answer is correct.

        Input args:
        - answer (int) : The index of the selected answer option.

        Return:
        - (bool) : True if the answer is correct, False otherwise.
        - (int)  : Number (0th indexed) of the correct answer
        '''
        # Check - has the quiz been correctly get?
        if self._quiz is None:
            raise RuntimeError('Quiz has not been initialized. Call _setup() first.')
        
        # Else checking the answer
        return self._quiz.check_answer(answer)
    
    
    def store_score(self) -> None:
        '''
        Adds the score to the database

        Input args:
        - None

        Return:
        - None
        '''
        # Check 1 - Has quiz been set?
        if self._quiz is None:
            raise RuntimeError('Quiz has not been initialized...')
        
        # Check 2 - Has the username been set?
        if not self._username:
            raise ValueError('Username is not set...')
        
        # Retrieves the quiz score and multiplies it by ten
        score = self._quiz.get_score() * 10

        # Constructing the quiz scores
        score_dict = {
            'username' : self._username,
            'score'    : score
        }
        
        # Database operation and its error handling (Game's responsibility to handle DB failure)
        try:
            self._db.add_record(collection_name = self._col_write, record = score_dict)
            print(f"Score for {self._username} ({score}) stored successfully.")

        # Catching exdeption thrown by database object
        except Exception as e: 
            print(f"ERROR: Failed to store score for {self._username}. Reason: {e}")
            raise 
    
    def has_question(self) -> bool:
        '''
        Checks if there are more questions in the quiz
        by delegating the call to the underlying Quiz object.

        Input args:
        - None

        Return:
        - (bool)
        '''
        # Chech - Has quiz been set?
        if self._quiz is None:
            return False
        
        # If so, returning actual value of quiz
        return self._quiz.has_question()
    
    def get_score(self) -> int:
        '''
        Pass-through method to retrieve the
        score for this quiz

        Input args:
        - None

        Return:
        - (int) : Score
        '''
        # Check - Has quiz been set?
        if self._quiz is None:
            return 0
        
        # If so, returning actual value of quiz
        return self._quiz.get_score()











