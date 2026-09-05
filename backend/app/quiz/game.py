from app.utils.database import Database
from app.quiz.question import Question
from app.quiz.quiz import Quiz
import numpy as np

class Game:
    '''
    Application layer that loads the
    quiz
    '''
    _db         = None
    _collection = None
    _hardness   = None
    _questions  = None

    _quiz = None

    _username = None

    _col_write = 'quiz_scores'


    def __init__(self, db : Database, collection : str, hardness : int,
                 questions : int, username : str) -> None:
        self._validate_db(db = db)
        self._validate_hardness(hardness = hardness)
        self._validate_questions(questions = questions)

        self._db         = db
        self._collection = collection
        self._questions  = questions
        self._hardness   = hardness
        self._username   = username

        self._setup()


    def _validate_db(self, db: Database) -> None:
        if not isinstance(db, Database):
            raise TypeError('The db argument must be an instance of the Database class.')

    def _validate_hardness(self, hardness: int) -> None:
        if not isinstance(hardness, int):
            raise TypeError('The hardness argument must be an integer.')

        if hardness not in [0, 1, 2]:
            raise ValueError('The hardness argument must be 0, 1, or 2.')

    def _validate_questions(self, questions: int) -> None:
        if not isinstance(questions, int):
            raise TypeError('The questions argument must be an integer.')

        if questions < 1:
            raise ValueError('The questions argument must be a positive integer.')

    def _validate_username(self, username: str) -> None:
        if not isinstance(username, str):
            raise TypeError('The username argument must be a string.')

        if not username.strip():
            raise ValueError('The username argument cannot be empty or just whitespace.')

    def _setup(self) -> None:
        query_hardness = {'level' : self._hardness}

        questions_list = self._db.get_records(collection_name = self._collection,
                                              query = query_hardness)

        if len(questions_list) == 0:
            raise ValueError('Failed to retrieve any questions of the appropriate hardness')

        n_selected = self._questions if len(questions_list) > self._questions else len(questions_list)

        n_available = np.arange(start = 0, stop = len(questions_list))

        index_selected = np.random.choice(n_available, n_selected, replace = False)

        question_list = []
        for i in index_selected:

            q = questions_list[i]

            question = Question(question = q['question'], answers = [q['A'], q['B'], q['C'], q['D']],
                                answer = q['answer'])
            question_list.append(question)

        self._quiz = Quiz(questions = question_list)

    def get_question(self) -> tuple:
        if self._quiz is None:
            raise RuntimeError('Quiz has not been initialized. Call _setup() first.')

        return self._quiz.get_question()

    def check_answer(self, answer: int) -> bool:
        if self._quiz is None:
            raise RuntimeError('Quiz has not been initialized. Call _setup() first.')

        return self._quiz.check_answer(answer)


    def store_score(self) -> None:
        if self._quiz is None:
            raise RuntimeError('Quiz has not been initialized...')

        if not self._username:
            raise ValueError('Username is not set...')

        score = self._quiz.get_score() * 10

        score_dict = {
            'username' : self._username,
            'score'    : score
        }

        try:
            self._db.add_record(collection_name = self._col_write, record = score_dict)
            print(f"Score for {self._username} ({score}) stored successfully.")

        except Exception as e:
            print(f"ERROR: Failed to store score for {self._username}. Reason: {e}")
            raise

    def has_question(self) -> bool:
        if self._quiz is None:
            return False

        return self._quiz.has_question()

    def get_score(self) -> int:
        if self._quiz is None:
            return 0

        return self._quiz.get_score()











