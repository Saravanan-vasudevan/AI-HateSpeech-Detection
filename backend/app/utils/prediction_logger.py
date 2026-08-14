# utils/prediction_logger.py

# Importing standard libraries
from datetime import datetime
import os
from dotenv import load_dotenv

# Importing the shared database connection class
from app.utils.database import Database

class PredictionLogger:
    '''
    PredictionLogger is responsible for logging the output of predictions into the MongoDB collection.

    It serves as a bridge between the ML prediction system and the persistent database, 
    allowing both model and human feedback to be stored with contextual information like 
    timestamp, user reason, and associated username.

    This class uses the `Database` utility to establish a secure connection to MongoDB,
    and logs each prediction into a dedicated collection named "predictions".
    '''

    def __init__(self):
        '''
        Initializes the PredictionLogger instance.

        - Loads the MongoDB connection credentials from `credentials.env`
        - Builds the MongoDB connection string
        - Establishes a database connection using the shared `Database` class
        - Initializes a reference to the 'predictions' collection
        '''

        # Load environment variables from the local credentials.env file
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.env')
        load_dotenv(dotenv_path=dotenv_path)

        # Read credentials from the environment
        db_password = os.getenv("DB_PASSWORD")
        db_string = os.getenv("DB_STRING")
        db_name = os.getenv("DB_NAME")

        # Replace <db_password> placeholder in connection string, if present
        if db_string and "<db_password>" in db_string and db_password:
            db_string = db_string.replace("<db_password>", db_password)

        # Initialize the Database connection
        self.db = Database(connection_string=db_string, db_name=db_name)

        # Get the 'predictions' collection handle for logging documents
        self.collection = self.db._get_collection("predictions")

    def log_prediction(
        self, 
        input_text: str, 
        label: str, 
        reason: str = None, 
        human_label: str = None, 
        username: str = None
    ) -> str:
        '''
        Logs a single prediction entry into the MongoDB "predictions" collection.

        Parameters:
        - input_text (str): The original text input submitted for prediction.
        - label (str): The label predicted by the AI model (e.g., 'hate' or 'not hate').
        - reason (str, optional): An optional explanation provided by the human user.
        - human_label (str, optional): An optional manual label provided by a human reviewer.
        - username (str, optional): The user’s identity, used for tracking and auditing.

        Returns:
        - str: The string representation of the inserted document’s ObjectId.
        '''

        # Construct the prediction document
        prediction_data = {
            "username": username,           # Optional user identity
            "timestamp": datetime.utcnow(), # Timestamp in UTC for consistency
            "input_text": input_text,       # Original text input
            "reason": reason,               # Optional explanation or justification
            "AI_label": label,              # AI model's label
            "Human_label": human_label,     # Optional human reviewer label
        }

        # Insert the prediction document into MongoDB and return the inserted ID
        result = self.collection.insert_one(prediction_data)
        return str(result.inserted_id)
