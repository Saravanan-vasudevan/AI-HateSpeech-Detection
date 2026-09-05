import os
from dotenv import load_dotenv
from pathlib import Path

from app.utils.database import Database
from app.quiz.quiz import Quiz
from app.quiz.game import Game

dotenv_path =  'credentials.env'

load_dotenv(dotenv_path = dotenv_path)

db_password = os.getenv('DB_PASSWORD')
db_string   = os.getenv('DB_STRING')

db_string = db_string.replace('<db_password>', db_password)

db_name = 'Hate_App'

db = Database(connection_string = db_string, db_name = db_name)

game = Game(db = db, collection = 'questions', questions = 5, hardness = 0)