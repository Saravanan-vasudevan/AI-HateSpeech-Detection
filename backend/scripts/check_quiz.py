# Importing custom pre-process text
import os
from dotenv import load_dotenv
from pathlib import Path

from app.utils.database import Database
from app.quiz.quiz import Quiz
from app.quiz.game import Game

# Constructin the path of the environment variable 
dotenv_path =  'credentials.env'

# Connecting to the correct environment path
load_dotenv(dotenv_path = dotenv_path)

# Retrieving properties of username
db_password = os.getenv('DB_PASSWORD')
db_string   = os.getenv('DB_STRING')

# Putting the password in the string
db_string = db_string.replace('<db_password>', db_password)

# Name of my database
db_name = 'Hate_App'
    
# Creating the database object
db = Database(connection_string = db_string, db_name = db_name)

# Creating a game
game = Game(db = db, collection = 'questions', questions = 5, hardness = 0)