import datetime
from dateutil.parser import parse as dateutil_parse
from app.history.predictions import Predictions # Assuming Predictions is in predictions.py
from app.history.prediction import Prediction   # Assuming Prediction is in prediction.py
from app.utils.database import Database       # Assuming Database is in database.py


class History:
    '''
    A class to retrieve and manage historical prediction records from a database.
    It fetches raw data and converts them into Prediction objects stored within
    a Predictions collection.
    '''

    # Attributes of the class
    _collection_name  = None # Name of collection to retrieve the data frome
    _db               = None # The database object to connect to

    def __init__(self, db_connection: Database, collection_name: str = 'predictions_history'):
        '''
        Initializes the History class with a database connection and the name
        of the collection where prediction records are stored.

        Input args:
        - db_connection (Database): An instance of the Database class.
        - collection_name (str): The name of the MongoDB collection storing prediction records.
    
        Raises:
        - TypeError: If db_connection is not an instance of the Database class.
        - ValueError: If collection_name is an empty or whitespace-only string.
        '''
        # Check - Do we have a database object to connect to? 
        if not isinstance(db_connection, Database):
            raise TypeError('db_connection must be an instance of the Database class.')
        
        # Check - Is the collection name a string with characters?
        if not isinstance(collection_name, str) or not collection_name.strip():
            raise ValueError('collection_name must be a non-empty string.')

        # Storing the predictions
        self._db              = db_connection
        self._collection_name = collection_name
        self._collection      = self._db._get_collection(self._collection_name)

    def retrieve_predictions(self, username: str = None, limit: int = 0) -> Predictions:
        '''
        Retrieves prediction records from the database and converts them into
        a Predictions object. Records are sorted by timestamp in descending order.

        Input args:
        - username (str, optional): Filters predictions by a specific username.
        - limit (int, optional)   : The maximum number of predictions to retrieve.

        Returns:
        - Predictions: A Predictions object containing the fetched records,
                       sorted by date in descending order. Returns an empty
                       Predictions object if no records are found or an error occurs.
        '''
        # Creating a blank query (as our starting point)
        query = {}

        # Check - Is username provided?
        if username is not None:

            # Check - Is the provied username actually a valid string with length?
            if not isinstance(username, str) or not username.strip():
                raise ValueError('Username must be a non-empty string if provided.')
            
            # If we get there, specifying the username for our query
            query['username'] = username

        # Define the sort order for retrieval: descending by timestamp
        sort_order = [('timestamp', -1)]

        # Fetch raw records from the database
        raw_records = self._db.get_records(
            collection_name = self._collection_name,
            query           = query,
            limit           = limit,
            sort            = sort_order
        )
        # List to store the objects
        prediction_objects = []

        # Iterating through the records
        for record in raw_records:
            try:
                
                # Performing the mapping
                pred = Prediction(
                    username          = record.get('username', 'N/A'),
                    datetime_str      = record.get('timestamp').isoformat() if record.get('timestamp') else datetime.datetime.now().isoformat(),
                    text              = record.get('text', ''),
                    human             = record.get('human', False),
                    ai                = record.get('ai', False),
                    human_explanation = record.get('human_explanation', ''),
                    ai_explanation    = record.get('ai_explanation', ''),
                    p                 = record.get('p', 0.0)
                )
                prediction_objects.append(pred)

            # Exception - Unable to manage a particular records
            except (ValueError, TypeError) as e:
                print(f"Skipping malformed record (ID: {record.get('_id')}): {e}")
            except Exception as e:
                print(f"An unexpected error occurred processing record (ID: {record.get('_id')}): {e}")

        # Initialize the Predictions collection with the retrieved Prediction objects
        return Predictions(initial_predictions = prediction_objects)
    
    def log_prediction(self, username : str, text: str, human : bool, ai : bool, human_explanation,
                       ai_explanation, p : float) -> str:
        '''
        Logs a single prediction entry into the MongoDB collection with a consistent schema.

        Input args:
        - username (str) : Username of user performing the prediction
        - text (str)     : Text that is being classified
        - human (bool)   : What the human predicted
        - ai (bool)      : What the AI model predicted
        - human_explanation (str) : Reason human thought it was as such
        - ai_explanation (str)    : Reason AI model thought it was such
        - p (float)               : Probability of being hate

        Return:
        - (str) : ID of inserted record
        '''
        # Create the document with field names that match the retrieve_predictions mapping
        prediction_data = {
            'username'          : username,
            'timestamp'         : datetime.datetime.utcnow(),
            'text'              : text,
            'human'             : human,
            'ai'                : ai,
            'human_explanation' : human_explanation,
            'ai_explanation'    : ai_explanation,
            'p'                 : p,
            'score'             : 10 if ai == human else 0
        }
        # Insert the document and storing its ID
        result = self._collection.insert_one(prediction_data)
    
        # Returning the ID
        return str(result.inserted_id)
    

    


