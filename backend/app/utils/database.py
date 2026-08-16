import pymongo
import pymongo.errors
from pymongo.read_concern import ReadConcern

import os
from dotenv import load_dotenv
from pathlib import Path

import math

class Database:
    '''
    A class to manage the connection to a MongoDB 
    Atlas database using PyMongo.
    '''
    def __init__(self, connection_string: str, db_name: str):
        '''
        Initializes the Database class with the MongoDB Atlas connection string
        and the name of the database to connect to.

        Args:
        - connection_string (str): The MongoDB Atlas connection string.
                                     (e.g., "mongodb+srv://user:pass@cluster.mongodb.net/retryWrites=true&w=majority")
        - db_name           (str): The name of the database to connect to within the cluster.
        '''
        self.connection_string = connection_string
        self.db_name           = db_name

        self.client = None
        self.db     = None

        self.__connect()

    def __connect(self) -> None:
        '''
        Establishes a connection to the MongoDB Atlas cluster.
        It has appropiate error handlin to mitigate the effect
        of credential / authentication issues

        Input args:
        - None

        Return:
        - None
        '''
        try:
        
            # Creating the client
            self.client = pymongo.MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS    = 30000,
                connectTimeoutMS            = 30000
            )


            self.client.admin.command('ping')

        
            self.db = self.client[self.db_name]

        # Exception 1:
        except pymongo.errors.ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")

            self.client = None
            self.db     = None
        
        #Exception 2: 
        except pymongo.errors.OperationFailure as e:
            print(f"MongoDB operation failed (e.g., authentication): {e}")

            self.client = None
            self.db     = None
        
        # Exception 3: 
        except Exception as e:
            print(f"An unexpected error occurred during connection: {e}")
            
            self.client = None
            self.db     = None

    def get_database(self) -> pymongo.database.Database:
        '''
        Returns the PyMongo database object if the connection is established.

        Returns:
        - pymongo.database.Database or None: The PyMongo database object, or None if not connected.
        '''

        if self.db is None:
            print('Database not connected. Please call .connect() first.')
        return self.db

    def close_connection(self) -> None:
        '''
        Closes the MongoDB connection.
        
        Input args:
        - None

        Return:
        - None
        '''
        if self.client:

            self.client.close()

            self.client = None
            self.db    = None
    def _get_collection(self, collection_name: str) -> pymongo.collection.Collection:
        '''
        Internal helper to get a collection object if the database is connected.
        It will default to none if it not connected at all

        Args:
        - collection_name (str): The name of the collection.

        Returns:
        - pymongo.collection.Collection or None: The collection object, or None if not connected/invalid name.
        '''
        # Check 1
        if self.db is None:
            return None
        
        return self.db[collection_name]

    def add_record(self, collection_name: str, record: dict) -> int:
        '''
        Adds a single record (document) to a specified collection.

        Args:
            collection_name (str): The name of the collection to add the record to.
            record (Dict[str, Any]): The dictionary representing the document to insert.

        Returns:
            Optional[Any]: The `inserted_id` of the new document, or None if the operation fails.
        '''
        collection = self._get_collection(collection_name)

        if collection is None:
            return None

        try:
            result = collection.insert_one(record)
            return result.inserted_id
        
        # Errror 1
        except pymongo.errors.PyMongoError as e:
            print(f"Error adding record to '{collection_name}': {e}")
            return None

        # Error 2 
        except Exception as e:
            print(f"An unexpected error occurred while adding record: {e}")
            return None
        
    def add_records(self, collection_name: str, records: list, batch_size: int = 100) -> list:
        '''
        Efficiently adds a list of records (documents) to a specified collection, with optional client-side batching.

        Args:
            collection_name (str): The name of the collection to add the records to.
            records (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
                                            represents a document to insert.
            batch_size (int, optional): The number of records to insert in each batch.
                                        Defaults to 100. Set to 0 or None to disable client-side batching
                                        and rely solely on PyMongo's internal batching.

        Returns:
            Optional[List[Any]]: A list of all `inserted_ids` for the new documents across all batches,
                                 or None if a critical error occurs that stops the entire operation.
                                 Returns an empty list if no records were provided or no IDs were inserted.
        '''
        collection = self._get_collection(collection_name)

        # Check 1 
        if collection is None:
            print(f"Error: Could not get collection '{collection_name}'. Database might not be connected.")
            return None

        # Check 2 
        if not records:
            print(f"No records provided to add to '{collection_name}'.")
            return []

        all_inserted_ids = []


        total_records        = len(records)
        effective_batch_size = batch_size if batch_size > 0 else total_records # Use total_records if batch_size is 0 or less

        num_batches = math.ceil(total_records / effective_batch_size)
       

        for i in range(0, total_records, effective_batch_size):

            batch = records[i:i + effective_batch_size]

            try:
                result = collection.insert_many(batch, ordered = False) 

                all_inserted_ids.extend(result.inserted_ids)
            
            except pymongo.errors.BulkWriteError as bwe:
                print(f"  Batch with records {id} completed with write errors. Details:")
                print(f"    Inserted count: {bwe.details.get('nInserted', 0)}")
                print(f"    Write errors: {bwe.details.get('writeErrors', [])}")

            except pymongo.errors.PyMongoError as e:
                print(f"  Error adding batch with record {i} to '{collection_name}': {e}")

            except Exception as e:
                print(f"  An unexpected error occurred while adding batch with record {i}: {e}")

        # Returning record
        return all_inserted_ids

    def get_record(self, collection_name: str, query: dict) -> dict:
        '''
        Retrieves a single record (document) from a specified collection based on a query.

        Args:
            collection_name (str): The name of the collection.
            query (Dict[str, Any]): A dictionary representing the query filter.

        Returns:
            Optional[Dict[str, Any]]: The found document as a dictionary, or None if not found or an error occurs.
        '''
        # Retrieving the collection
        collection = self._get_collection(collection_name)

        # Checking if the collection is valid
        if collection is None:
            return None

        # Attempting to retrieve a record
        try:

            record = collection.find_one(query)

            if record is None:
                print(f"No record found in '{collection_name}' matching query: {query}")
            
            return record
        
        except pymongo.errors.PyMongoError as e:
            print(f"Error getting record from '{collection_name}' with query {query}: {e}")
            return None
        
        except Exception as e:
            print(f"An unexpected error occurred while getting record: {e}")
            return None

    def get_records(self, collection_name: str, query: dict = None,
                    projection: dict = None, limit: int = 0, sort: dict = None) -> list:
        '''
        Retrieves multiple records (documents) from a specified collection based on a query.

        Args:
            collection_name (str): The name of the collection.
            query (Dict[str, Any], optional): A dictionary representing the query filter. Defaults to None (all documents).
            projection (Dict[str, Any], optional): A dictionary specifying fields to include/exclude.
                                                   e.g., {"field_name": 1, "_id": 0}. Defaults to None (all fields).
            limit (int, optional): The maximum number of documents to return. 0 means no limit. Defaults to 0.
            sort (Dict[str, Any], optional): A dictionary specifying the sort order.
                                             e.g., {"field_name": 1} for ascending, {"field_name": -1} for descending.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary is a document.
                                  Returns an empty list if no records are found or an error occurs.
        '''
        collection = self._get_collection(collection_name)

        if collection is None:
            return []

        if query is None:
            query = {}

        try:
            cursor = collection.find(query, projection)
            
            if sort:
                cursor = cursor.sort(sort)

            if limit > 0:
                cursor = cursor.limit(limit)

            return list(cursor)
        
        except pymongo.errors.PyMongoError as e:
            print(f"Error getting records from '{collection_name}' with query {query}: {e}")
            return []
        
        except Exception as e:
            print(f"An unexpected error occurred while getting records: {e}")
            return []
        
if __name__ == '__main__':

    project_root = Path(__file__).resolve().parents[1]

    dotenv_path = project_root / 'credentials.env'

    load_dotenv(dotenv_path = dotenv_path)

    # Retrieving properties of username
    db_password = os.getenv('DB_PASSWORD')
    db_string   = os.getenv('DB_STRING')

    # Putting the password in the string
    db_string = db_string.replace('<db_password>', db_password)

    db_name = 'Hate_App'
    
    db = Database(connection_string = db_string, db_name = db_name)

    # Dummy user record
    user_record = {
        'email'    : 'test@gmail.com',
        'password' : 'hello1234'
    }
    # Adding user
    db.add_record(collection_name = 'users', record = user_record)

    # Records of text
    texts = [
        {'text' : 'Hello, how are you?', 'label' : 1, 'datset' : 'Dynabench'},
        {'text' : 'Hello, how are you?', 'label' : 0, 'datset' : 'Dynabench'},
        {'text' : 'Hello, how are you?', 'label' : 0, 'datset' : 'Dynabench'}
    ]
    db.add_records(collection_name = 'text', records = texts, batch_size = 2)

