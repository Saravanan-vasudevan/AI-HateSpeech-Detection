# Importing relevant libraries
from sklearn.model_selection import train_test_split
import os
from dotenv import load_dotenv
from app.utils.database import Database
import pandas as pd

# Constructin the path of the environment variable 
dotenv_path = 'credentials.env'

# Connecting to the correct environment path
load_dotenv(dotenv_path = dotenv_path)

# Extracting relevant database properties
# Retrieving properties of username
db_password = os.getenv('DB_PASSWORD')
db_string   = os.getenv('DB_STRING')

# Putting the password in the string
db_string = db_string.replace('<db_password>', db_password)

# Name of my database
db_name = 'Hate_App'
    
# Creating the database object
db = Database(connection_string = db_string, db_name = db_name)

# Name of collection with data
col_data = 'text'

# Query for English
query_english = {'language' : {'$eq' : 'English'}}

# Retrieving the data
eng_dict = db.get_records(collection_name = col_data, query = query_english)

# Converting into a dataframe
df = pd.DataFrame(eng_dict)

# Label is the target
y = df['label'].to_list()

# Selecting the featues
X = df['text'].to_list()

# Splitting the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)

# Putting into a test dataframe
df_test = pd.DataFrame(
    data = {
        'X' : X_test,
        'y' : y_test
    }
)
# Saving the data
df_test.to_csv('evaluate/test_data.csv')

