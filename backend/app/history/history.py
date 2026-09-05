import datetime
from dateutil.parser import parse as dateutil_parse
from app.history.predictions import Predictions
from app.history.prediction import Prediction
from app.utils.database import Database


class History:
    '''
    A class to retrieve and manage historical prediction records from a database.
    It fetches raw data and converts them into Prediction objects stored within
    a Predictions collection.
    '''

    _collection_name  = None
    _db               = None

    def __init__(self, db_connection: Database, collection_name: str = 'predictions_history'):
        if not isinstance(db_connection, Database):
            raise TypeError('db_connection must be an instance of the Database class.')

        if not isinstance(collection_name, str) or not collection_name.strip():
            raise ValueError('collection_name must be a non-empty string.')

        self._db              = db_connection
        self._collection_name = collection_name
        self._collection      = self._db._get_collection(self._collection_name)

    def retrieve_predictions(self, username: str = None, limit: int = 0) -> Predictions:
        query = {}

        if username is not None:

            if not isinstance(username, str) or not username.strip():
                raise ValueError('Username must be a non-empty string if provided.')

            query['username'] = username

        sort_order = [('timestamp', -1)]

        raw_records = self._db.get_records(
            collection_name = self._collection_name,
            query           = query,
            limit           = limit,
            sort            = sort_order
        )
        prediction_objects = []

        for record in raw_records:
            try:

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

            except (ValueError, TypeError) as e:
                print(f"Skipping malformed record (ID: {record.get('_id')}): {e}")
            except Exception as e:
                print(f"An unexpected error occurred processing record (ID: {record.get('_id')}): {e}")

        return Predictions(initial_predictions = prediction_objects)

    def log_prediction(self, username : str, text: str, human : bool, ai : bool, human_explanation,
                       ai_explanation, p : float) -> str:
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
        result = self._collection.insert_one(prediction_data)

        return str(result.inserted_id)





