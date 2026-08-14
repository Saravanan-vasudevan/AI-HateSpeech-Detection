# backend/utils/iam.py
# Importing database functionality
from app.utils.database import Database

# Importing user class
from app.utils.user import User

# Regular expressions
import re

# Ability to check / hash passwords
import bcrypt

# Functionality to determine environment variables
import os
from dotenv import load_dotenv
from pathlib import Path

class IAM:
    '''
    Identity and access management
    tool that logs a user in
    '''
    # Properties of the object
    db              = None    # Stores the data object
    db_collection = 'user'  # Name of collection where users are stored

    def __init__(self, db : Database) -> None:
        '''
        Sets up the database for logging in
        and out, as well as registration

        Input args:
        - db (Database) : Database object for use

        Return:
        - None
        '''
        # Storing the database
        self.db = db

    def _hash_password(self, password : str) -> bytes: # Fix: Return type hint is bytes
        '''
        Hashes a password using the bcrypt library

        Input args:
        - password (str) : Password to check

        Return:
        - (bytes) : Hashed passwords
        '''
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def _check_hashed_password(self, password : str, hashed_password : bytes) -> bool: # Fix: hashed_password type hint is bytes
        '''
        Checks if a password matches a hashed password.

        Inputs args:
        - password (str) : Candidate password
        - hashed_password (bytes) : Actual password, hashed (must be bytes from bcrypt)

        Return:
        - (bool) : True if password is correct
        '''
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def check_user(self, username : str, password : str) -> bool:
        '''
        Checks if the provided username and password are correct.

        Args:
            username (str): The username to check.
            password (str): The plain-text password to check.

        Returns:
            bool: True if the username and password are correct, False otherwise.
        '''
        # Constructing the query
        user_query = {'username' : username}

        try:
            # Check 1 - Is the username correct?
            users = self.db.get_records(collection_name = self.db_collection, query = user_query)
        except Exception: # Catch any database errors
            return False # Or re-raise a custom exception for more specific handling

        # ... If there was a user
        if len(users) > 0:
            # Retrieving the 1st record (the record)
            user_data = users[0]

            # Fix: Ensure the stored password is converted to bytes BEFORE calling _check_hashed_password
            stored_password = user_data['password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')

            # Checking the user's password
            if self._check_hashed_password(password, stored_password):
                return True

        # Else, user will be false
        return False

    def get_user(self, username : str) -> User:
        '''
        Retrieves a User object if the username exists.

        Args:
        - username (str): The username to retrieve.

        Returns:
        - User or None: A User object if the user exists, None otherwise.
        '''
        # Query to search the data
        query_user = {'username' : username}

        try:
            # Fix: Use keyword argument for collection_name
            user_data_list = self.db.get_records(collection_name=self.db_collection, query=query_user)
        except Exception: # Fix: Add try-except block to handle DB errors gracefully
            return None

        # Checking if user has been retrieved
        if len(user_data_list) > 0:
            # Extracting a user
            user = user_data_list[0]

            # Creating a user
            try:
                user_profile = User(
                    username = user.get('username'),
                    first_name = user.get('first_name'),
                    last_name = user.get('last_name'),
                    admin = user.get('admin', False) # Default admin to False if not present
                )
                # Returning the user profile
                return user_profile
            except Exception as e: # Catch any potential errors during User object creation
                print(f'Error creating User object due to data: {e}')
                return None # Return None if User object can't be created

        # ... Else, returning a None object
        return None

    def is_suitable(self, username : str, password : str) -> tuple:
        '''
        Checks if a username and password meet the suitability requirements.

        Input args:
        - username (str) : Candidate username
        - password (str) : Candidate password

        Retun:
        - (bool) : True if username is suitable and available, and password
        - (str)  : User message that can be used as a warning message

        Requirements:
        - Username:
            - At least 3 characters long.
            - Only alphanumeric characters and underscores.
            - Must be unique in the database.
        - Password:
            - At least 8 characters long.
            - Contains at least one uppercase letter.
            - Contains at least one lowercase letter.
            - Contains at least one digit.
            - Contains at least one special character (e.g., !@#$%^&*()).
        '''
        # Username suitability checks
        if len(username) < 3:
            return False, 'Username must be at least 3 characters long.'
        if not re.fullmatch(r'^[a-zA-Z0-9_]+$', username):
            return False, 'Username can only contain alphanumeric characters and underscores.'

        # Check for username uniqueness
        user_query = {'username' : username}
        try:
            # Fix: Use keyword argument for collection_name
            users = self.db.get_records(collection_name=self.db_collection, query=user_query)
            if len(users) > 0:
                return False, 'Username is not available'
        except Exception: # Fix: Add try-except block to handle DB errors gracefully
            return False, 'Error checking username availability.'


        # Password suitability checks
        if len(password) < 8:
            return False, 'Password must be at least 8 characters long.'
        if not re.search(r'[A-Z]', password):
            return False, 'Password must contain at least one uppercase letter.'
        if not re.search(r'[a-z]', password):
            return False, 'Password must contain at least one lowercase letter.'
        if not re.search(r'\d', password):
            return False, 'Password must contain at least one digit.'
        if not re.search(r'[!@#$%^&*()]', password):
            return False, 'Password must contain at least one special character (!@#$%^&*()).'

        # Else, we have returned to the end
        return True, ''

    def create_user(self, username : str, password : str, first_name : str,
                    last_name : str, admin : bool) -> tuple: # Fix: Return type hint is tuple
        '''
        Creates a new user record in the database after checking suitability.

        Args:
            username (str): The username for the new user.
            password (str): The plain-text password for the new user.
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            admin (bool): Whether the user is an admin.

        Returns:
            tuple: (bool, str) - True and 'User created successfully' if successful,
                                 False and an error message otherwise.
        '''
        try: # Fix: Add try-except block to handle errors gracefully
            # Hashing the password for user
            hashed_password = self._hash_password(password)

            # Constructing the user dictionary
            user_dict = {
                'username'   : username,
                'password'   : hashed_password,
                'first_name' : first_name,
                'last_name'  : last_name,
                'admin'      : admin
            }
            # Adding the user
            self.db.add_record(collection_name = self.db_collection, record = user_dict)
            return True, 'User created successfully.'
        
        except Exception as e:

            # Catch potential errors from hashing or database operations
            return False, f'Failed to create user: {e}'