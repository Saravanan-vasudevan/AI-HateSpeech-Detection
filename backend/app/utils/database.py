# Importing PyMongo
import pymongo
import pymongo.errors
from pymongo.read_concern import ReadConcern

# Functionality to determine environment variables
import os
from dotenv import load_dotenv
from pathlib import Path

# Importing math library (needed for rounding up
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
                                     (e.g., "mongodb+srv://username:<db_password>@cluster.example.mongodb.net/")
        - db_name           (str): The name of the database to connect to within the cluster.
        '''
        # Storing the attributes of the database
        self.connection_string = connection_string
        self.db_name           = db_name

        # Connections (These need to be determined)
        self.client = None
        self.db     = None

        # Calling the connect method
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
        # N.B - There are variou points of failure
        #       Hence, method is encapsulated in try / catch
        try:
        
            # Creating the client
            self.client = pymongo.MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS    = 30000,
                connectTimeoutMS            = 30000
            )


            # The ping command is cheap and does not require auth.
            # It confirms that the connection is working.
            self.client.admin.command('ping')

            # Connecting to the database itself
            # N.B: If access is sufficient, it will actually create the database
            # This will only be done by admin
            self.db = self.client[self.db_name]

        # Exception 1: Connection failure
        except pymongo.errors.ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")

            # Defaulting the client to empty objects
            self.client = None
            self.db     = None
        
        #Exception 2: Operation failure (often authentication)
        except pymongo.errors.OperationFailure as e:
            print(f"MongoDB operation failed (e.g., authentication): {e}")

            # Resetting the clien to null object
            self.client = None
            self.db     = None
        
        # Exception 3: Anything not covered already
        except Exception as e:
            print(f"An unexpected error occurred during connection: {e}")
            
            # Defaulting the client and database
            self.client = None
            self.db     = None

    def get_database(self) -> pymongo.database.Database:
        '''
        Returns the PyMongo database object if the connection is established.

        Returns:
        - pymongo.database.Database or None: The PyMongo database object, or None if not connected.
        '''
        # Checking if the database is connected
        # This could be due to connection closure or connection error
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
        # Checking if the database client is connected
        if self.client:

            # ... Closing the object
            self.client.close()

            # ... Defaulting the connection objects
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
        # Check 1 - Is the database actually connected?
        if self.db is None:
            return None
        
        # Else, returning the collection
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
        # Retrieving the collection
        collection = self._get_collection(collection_name)

        # Checking the collection is valid
        # If not, do not attempting to connect
        if collection is None:
            return None

        # Else, performing the insertion
        try:
            result = collection.insert_one(record)
            return result.inserted_id
        
        # Errror 1- a PyMongoError
        except pymongo.errors.PyMongoError as e:
            print(f"Error adding record to '{collection_name}': {e}")
            return None

        # Error 2 - An unhandled error
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
        # Attempting to retrieve the collection
        collection = self._get_collection(collection_name)

        # Check 1 - Could a collection actually be retrieved?
        if collection is None:
            print(f"Error: Could not get collection '{collection_name}'. Database might not be connected.")
            return None

        # Check 2 - Where no records actually passed?
        if not records:
            print(f"No records provided to add to '{collection_name}'.")
            return []

        # List of the records that have been added
        all_inserted_ids = []

        # Determining the number of records and batch size
        # This is needed, as it might not actually be necessary
        # to batch records if we're not using them
        total_records        = len(records)
        effective_batch_size = batch_size if batch_size > 0 else total_records # Use total_records if batch_size is 0 or less

        # Calculate total number of batches for progress reporting
        num_batches = math.ceil(total_records / effective_batch_size)
       

        # Iterating throuh the batches
        for i in range(0, total_records, effective_batch_size):

            # Retrieving the batch
            batch = records[i:i + effective_batch_size]

            # Attempting to perform the insertion
            try:
                result = collection.insert_many(batch, ordered = False) 

                # Updating the list of records
                all_inserted_ids.extend(result.inserted_ids)
            
            # Errror 1 - Something went wrong with bulk write
            except pymongo.errors.BulkWriteError as bwe:
                # This error occurs when some inserts succeed and some fail in an unordered operation
                print(f"  Batch with records {id} completed with write errors. Details:")
                print(f"    Inserted count: {bwe.details.get('nInserted', 0)}")
                print(f"    Write errors: {bwe.details.get('writeErrors', [])}")

            # Error 2 - Other PyMongo error
            except pymongo.errors.PyMongoError as e:
                print(f"  Error adding batch with record {i} to '{collection_name}': {e}")

            # Error 3 - Unhandled exception
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

            # Passing the query for the record
            record = collection.find_one(query)

            # Checking record found
            if record is None:
                print(f"No record found in '{collection_name}' matching query: {query}")
            
            # Returning the record
            return record
        
        # Check 1 - An error from the PyMongo client
        except pymongo.errors.PyMongoError as e:
            print(f"Error getting record from '{collection_name}' with query {query}: {e}")
            return None
        
        # Check 2 - Some unhandled error
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
        # Attempting to retrieve the collection
        collection = self._get_collection(collection_name)

        # In unable to find the collection, returning none
        if collection is None:
            return []

        # If no query found, creating an empty query (all records)
        if query is None:
            query = {}

        # Checking our query
        try:
            cursor = collection.find(query, projection)
            
            if sort:
                cursor = cursor.sort(sort)

            # Apply a limit if it's a positive number
            if limit > 0:
                cursor = cursor.limit(limit)

            # Return the results as a list of dictionaries
            return list(cursor)
        
        # Check - Errors from PyMongo
        except pymongo.errors.PyMongoError as e:
            print(f"Error getting records from '{collection_name}' with query {query}: {e}")
            return []
        
        # Check - Any other errors
        except Exception as e:
            print(f"An unexpected error occurred while getting records: {e}")
            return []
        
# Checkin error
if __name__ == '__main__':

    # Ensrung we're at the root of the project
    project_root = Path(__file__).resolve().parents[1]

    # Constructin the path of the environment variable 
    dotenv_path = project_root / 'credentials.env'

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

