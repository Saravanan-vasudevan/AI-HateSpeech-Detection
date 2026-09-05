from sklearn.model_selection import train_test_split
import os
from dotenv import load_dotenv
from app.utils.database import Database
import pandas as pd

dotenv_path = 'credentials.env'

load_dotenv(dotenv_path = dotenv_path)

db_password = os.getenv('DB_PASSWORD')
db_string   = os.getenv('DB_STRING')

db_string = db_string.replace('<db_password>', db_password)

db_name = 'Hate_App'

db = Database(connection_string = db_string, db_name = db_name)

col_data = 'text'

query_english = {'language' : {'$eq' : 'English'}}

eng_dict = db.get_records(collection_name = col_data, query = query_english)

df = pd.DataFrame(eng_dict)

y = df['label'].to_list()

X = df['text'].to_list()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)

df_test = pd.DataFrame(
    data = {
        'X' : X_test,
        'y' : y_test
    }
)
df_test.to_csv('evaluate/test_data.csv')

