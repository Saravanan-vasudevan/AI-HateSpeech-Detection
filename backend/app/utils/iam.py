from app.utils.database import Database

from app.utils.user import User

import re

import bcrypt

import os
from dotenv import load_dotenv
from pathlib import Path

class IAM:
    '''
    Identity and access management
    tool that logs a user in
    '''
    db              = None
    db_collection = 'user'

    def __init__(self, db : Database) -> None:
        self.db = db

    def _hash_password(self, password : str) -> bytes:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def _check_hashed_password(self, password : str, hashed_password : bytes) -> bool:
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
        user_query = {'username' : username}

        try:
            users = self.db.get_records(collection_name = self.db_collection, query = user_query)
        except Exception:
            return False

        if len(users) > 0:
            user_data = users[0]

            stored_password = user_data['password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')

            if self._check_hashed_password(password, stored_password):
                return True

        return False

    def get_user(self, username : str) -> User:
        '''
        Retrieves a User object if the username exists.

        Args:
        - username (str): The username to retrieve.

        Returns:
        - User or None: A User object if the user exists, None otherwise.
        '''
        query_user = {'username' : username}

        try:
            user_data_list = self.db.get_records(collection_name=self.db_collection, query=query_user)
        except Exception:
            return None

        if len(user_data_list) > 0:
            user = user_data_list[0]

            try:
                user_profile = User(
                    username = user.get('username'),
                    first_name = user.get('first_name'),
                    last_name = user.get('last_name'),
                    admin = user.get('admin', False)
                )
                return user_profile
            except Exception as e:
                print(f'Error creating User object due to data: {e}')
                return None

        return None

    def is_suitable(self, username : str, password : str) -> tuple:
        if len(username) < 3:
            return False, 'Username must be at least 3 characters long.'
        if not re.fullmatch(r'^[a-zA-Z0-9_]+$', username):
            return False, 'Username can only contain alphanumeric characters and underscores.'

        user_query = {'username' : username}
        try:
            users = self.db.get_records(collection_name=self.db_collection, query=user_query)
            if len(users) > 0:
                return False, 'Username is not available'
        except Exception:
            return False, 'Error checking username availability.'


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


        return True, ''

    def create_user(self, username : str, password : str, first_name : str,
                    last_name : str, admin : bool) -> tuple:
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
        try:
            hashed_password = self._hash_password(password)


            user_dict = {
                'username'   : username,
                'password'   : hashed_password,
                'first_name' : first_name,
                'last_name'  : last_name,
                'admin'      : admin
            }
            self.db.add_record(collection_name = self.db_collection, record = user_dict)
            return True, 'User created successfully.'

        except Exception as e:

            return False, f'Failed to create user: {e}'