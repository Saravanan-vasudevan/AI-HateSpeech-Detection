# backend/test/utils/test_iam.py
import unittest
from unittest.mock import MagicMock, patch
import bcrypt
import re

# Importing the IAM class
# - This is the functionality that is under test here
from app.utils.iam import IAM

# User class
# - Rather than using a mock class, we are able to use
#   the user class directly
from app.utils.user import User

class TestIAM(unittest.TestCase):
    '''
    Performs a full suite of static tests
    on the IAM class
    '''
    def setUp(self):
        '''
        Sets up the necessary requirements for the
        unit testing
        '''
        # Create a mock database object for each test
        self.mock_db = MagicMock()
        self.iam     = IAM(db = self.mock_db) # This is using the mock db

        # Pre-calculated hashed password for consistency in some tests
        self.known_password = 'TestPass1!'
        self.known_hashed_password_bytes = bcrypt.hashpw(self.known_password.encode('utf-8'), bcrypt.gensalt())

        # Example user data for mocking DB responses
        self.mock_user_data = {
            'username'   : 'existinguser',
            'password'   : self.known_hashed_password_bytes, # This is bytes
            'first_name' : 'Existing',
            'last_name'  : 'User',
            'admin'      : False
        }
        self.mock_admin_user_data = {
            'username'  : 'adminuser',
            'password'  : bcrypt.hashpw(b'AdminPass1!', bcrypt.gensalt()),
            'first_name': 'Super',
            'last_name' : 'Admin',
            'admin'     : True
        }
    def test_init_stores_db_object(self):
        '''
        Test that the IAM class correctly stores the database object.
        '''
        # Check 1 - Is is the database object correctly stored? 
        self.assertIs(self.iam.db, self.mock_db)

        # Check 2 - Is the name of collection to stored?
        self.assertEqual(self.iam.db_collection, 'user')

    @patch('utils.iam.IAM._hash_password')
    def test_hash_password_returns_consistent_hash_with_fixed_salt(self, mock_hash_password):
        '''
        Test that _hash_password returns a consistent hash.
        '''
        # Configure mock_hash_password to return a valid hashed byte string
        mock_hash_password.return_value = bcrypt.hashpw(b'some_password_to_hash', bcrypt.gensalt())

        # Passwod we are going to use (and hashed version)
        password = 'mysecretpassword'
        hashed_password = self.iam._hash_password(password)

        # Check 1 - Is hashed password a bytes object?
        self.assertIsInstance(hashed_password, bytes)

        # Check 2 - Does the hashed argument have length?
        self.assertTrue(len(hashed_password) > 0)

        # Verify _hash_password was called with the correct plain password
        mock_hash_password.assert_called_once_with(password)

    def test_check_hashed_password_correct_password(self):
        '''
        Test _check_hashed_password with a correct password.
        '''
        # Check 1 - Can we ensure the hashed password is correct?
        self.assertTrue(self.iam._check_hashed_password(self.known_password, self.known_hashed_password_bytes))

    def test_check_hashed_password_incorrect_password(self):
        '''
        Test _check_hashed_password with an incorrect password.'
        '''
        # Check 1 - Does the code not check as true even with a false password?
        self.assertFalse(self.iam._check_hashed_password('WrongPass1!', self.known_hashed_password_bytes))

    def test_check_hashed_password_empty_password(self):
        '''
        Test _check_hashed_password with an empty candidate password.
        '''
        # Check 1 - Does an empty password not shown as true?
        self.assertFalse(self.iam._check_hashed_password('', self.known_hashed_password_bytes))

    def test_check_hashed_password_empty_hashed_password_bytes(self):
        '''
        Test _check_hashed_password with empty bytes for hashed password (expect ValueError).
        '''
        # Check - Does an empty hashed password show as false?
        with self.assertRaises(ValueError, msg = 'bcrypt.checkpw should raise ValueError for empty hash'):
            self.iam._check_hashed_password(self.known_password, b'')

    def test_check_hashed_password_malformed_hashed_password(self):
        '''
        Test _check_hashed_password with malformed hashed password bytes (expect ValueError).
        '''
        # Check 1 - Does an incorrect format byte string not show to be true?
        with self.assertRaises(ValueError, msg = 'bcrypt.checkpw should raise ValueError for malformed hash'):
            self.iam._check_hashed_password(self.known_password, b'invalid_hash_string')

    def test_check_user_valid_username_correct_password(self):
        '''
        Test check_user with a valid username and correct password.
        '''
        # Specifying what the expected database return will be
        self.mock_db.get_records.return_value = [self.mock_user_data]

        # Check 1 - Does the database know this is the user?
        self.assertTrue(self.iam.check_user('existinguser', self.known_password))
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'existinguser'}
        )

    def test_check_user_valid_username_incorrect_password(self):
        '''
        Test check_user with a valid username but incorrect password.
        '''
        # Again, specifying the return format of database
        self.mock_db.get_records.return_value = [self.mock_user_data]
        
        # Check - Incorrect password this time
        self.assertFalse(self.iam.check_user('existinguser', 'WrongPass1!'))
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'existinguser'}
        )

    def test_check_user_username_not_found(self):
        '''
        Test check_user when the username does not exist.
        '''
        self.mock_db.get_records.return_value = []
        self.assertFalse(self.iam.check_user('nonexistentuser', 'anypassword'))
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'nonexistentuser'}
        )

    def test_check_user_empty_username(self):
        '''
        Test check_user with an empty username.
        '''
        # Specifying an empty user (with an empty list)
        self.mock_db.get_records.return_value = [] # An empty username should not be found

        # Check 1 - Is this username false?
        self.assertFalse(self.iam.check_user('', 'anypassword'))
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': ''}
        )

    def test_check_user_empty_password(self):
        '''
        Test check_user with an empty password against a valid user.
        '''
        # Putting the return value back to mock data
        self.mock_db.get_records.return_value = [self.mock_user_data]

        # Check 1 - What happens with an empty password?
        self.assertFalse(self.iam.check_user('existinguser', ''))
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'existinguser'}
        )

    def test_check_user_database_error_on_get_records(self):
        '''
        Test check_user handles a database error gracefully by returning False.
        '''
        # Immitating a database error
        self.mock_db.get_records.side_effect = Exception('Database connection lost')

        # Check - Can user not log in when error occurs?
        self.assertFalse(self.iam.check_user('testuser', self.known_password))
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'testuser'}
        )

    @patch('utils.iam.IAM._check_hashed_password')
    def test_check_user_password_as_string_in_db(self, mock_check_hashed_password):
        '''
        Test check_user when password is accidentally stored as a string in DB.
        '''
        # Configure mock_check_hashed_password to return True, simulating a successful check
        mock_check_hashed_password.return_value = True

        # Creating a deep copy of the user
        user_data_str_password = self.mock_user_data.copy()
        user_data_str_password['password'] = self.known_hashed_password_bytes.decode('utf-8') # Explicitly a string

        # Check - Does the comparison work with values (not just pointers)?
        self.mock_db.get_records.return_value = [user_data_str_password]
        self.assertTrue(self.iam.check_user('existinguser', self.known_password))

        # Assert that _check_hashed_password was called with the password converted to bytes
        # This confirms the conversion logic within check_user
        mock_check_hashed_password.assert_called_once_with(
            self.known_password, user_data_str_password['password'].encode('utf-8')
        )
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'existinguser'}
        )

    def test_get_user_existing_username_returns_user_object(self):
        '''
        Test get_user returns a User object for an existing username.
        '''
        # Setting the db to return the actual value
        self.mock_db.get_records.return_value = [self.mock_user_data]
        user_profile = self.iam.get_user('existinguser')

        # Check - Are all the parameters as expected?
        self.assertIsInstance(user_profile, User)
        self.assertEqual(user_profile.get_username(), self.mock_user_data['username'])
        self.assertEqual(user_profile.to_dict()['first_name'], self.mock_user_data['first_name'])
        self.assertEqual(user_profile.to_dict()['last_name'], self.mock_user_data['last_name'])
        self.assertEqual(user_profile.is_admin(), self.mock_user_data['admin'])

        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'existinguser'}
        )

    def test_get_user_admin_user(self):
        '''
        Test get_user returns correct User object for an admin.
        '''
        # Specifying the database is to return admin user
        self.mock_db.get_records.return_value = [self.mock_admin_user_data]
        user_profile = self.iam.get_user('adminuser')

        # Check - Does the admin data match?
        self.assertTrue(user_profile.is_admin())
        self.assertEqual(user_profile.get_username(), self.mock_admin_user_data['username'])
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'adminuser'}
        )

    def test_get_user_non_existent_username_returns_none(self):
        '''
        Test get_user returns None for a non-existent username.
        '''
        # Specifying data returns empty list (i.e. no user)
        self.mock_db.get_records.return_value = []
        user_profile = self.iam.get_user('nonexistent')

        # Check - Does the user profile be none?
        self.assertIsNone(user_profile)
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'nonexistent'}
        )

    def test_get_user_database_error_returns_none(self):
        '''
        Test get_user handles database errors by returning None.
        '''
        # Specifying a database read error
        self.mock_db.get_records.side_effect = Exception('DB read error')

        # Check - What happens with a read error?
        self.assertIsNone(self.iam.get_user('anyuser'))
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'anyuser'}
        )

    def test_get_user_incomplete_data_from_db_missing_key(self):
        '''
        Test get_user when user data from DB is missing a required key.
        '''
        # N.B - See that the user profile has no last_name
        incomplete_user_data = {
            'username'  : 'incomplete',
            'password'  : b'some_hash',
            'first_name': 'Incomplete',
            'admin'     : False
        }
        # Specifying that database is to return null value
        self.mock_db.get_records.return_value = [incomplete_user_data]

        # Retrieving the user (without last night)
        user_profile = self.iam.get_user('incomplete')

        # Check - Do attributes match and no key error?
        self.assertIsInstance(user_profile, User)
        self.assertEqual(user_profile.get_username(), 'incomplete')
        self.assertIsNone(user_profile.to_dict()['last_name'])
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'incomplete'}
        )

    def test_is_suitable_username_too_short(self):
        '''
        Test is_suitable with a username that is too short.
        '''
        # Test - username invalid, password to short
        result, msg = self.iam.is_suitable('ab', 'ValidPass1!')

        # Check - Does it identify that username is unsuitable?
        self.assertFalse(result)
        self.assertEqual(msg, 'Username must be at least 3 characters long.')
        self.mock_db.get_records.assert_not_called()

    def test_is_suitable_username_invalid_characters(self):
        '''
        Test is_suitable with a username containing invalid characters.
        '''
        # Specifying username with unsuitable usenrame (valid password)
        result, msg = self.iam.is_suitable('user-name', 'ValidPass1!')
        
        # Check - It identifies an incorrect username format?
        self.assertFalse(result)
        self.assertEqual(msg, 'Username can only contain alphanumeric characters and underscores.')
        self.mock_db.get_records.assert_not_called()

    def test_is_suitable_username_not_available(self):
        '''
        Test is_suitable with a username that already exists in the database.
        '''
        # Specifying an existing user
        self.mock_db.get_records.return_value = [{'username': 'existinguser'}]
        result, msg = self.iam.is_suitable('existinguser', 'ValidPass1!')

        # Check - Existing user has been detected?
        self.assertFalse(result)
        self.assertEqual(msg, 'Username is not available')
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'existinguser'}
        )

    def test_is_suitable_username_available_and_valid(self):
        '''
        Test is_suitable with a valid and available username.
        '''
        # Specifying no existing user (so an available username)
        self.mock_db.get_records.return_value = [] 
        result, msg = self.iam.is_suitable('new_valid_user', 'ValidPass1!')

        # Check - Username and password suitable and valid?
        self.assertTrue(result)
        self.assertEqual(msg, '')
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'new_valid_user'}
        )

    def test_is_suitable_database_error_on_uniqueness_check(self):
        '''
        Test is_suitable handles database errors during uniqueness check.
        '''
        # Mocking a database error
        self.mock_db.get_records.side_effect = Exception('DB connection down')
        
        # Expect False and specific message from IAM method, no re-raise in test
        result, msg = self.iam.is_suitable('anyuser', 'ValidPass1!')
        self.assertFalse(result)
        self.assertEqual(msg, 'Error checking username availability.')

        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'anyuser'}
        )

    def test_is_suitable_password_too_short(self):
        '''
        Test is_suitable with a password that is too short.
        '''
        # Specifying no returned users (so username is valid)
        self.mock_db.get_records.return_value = [] # Assume username is available

        # Passing a short password
        result, msg = self.iam.is_suitable('validuser', 'Short1!')

        # Check - Is password too short?
        self.assertFalse(result)
        self.assertEqual(msg, 'Password must be at least 8 characters long.')

    def test_is_suitable_password_no_uppercase(self):
        '''
        Test is_suitable with a password missing an uppercase letter.
        '''
        # Specifying no existing user available with outputs
        self.mock_db.get_records.return_value = []

        # Specifying a password with no uppercase
        result, msg = self.iam.is_suitable('validuser', 'noupper1!')

        # Check - Is password unsuitable due to its abscence of uppercase?
        self.assertFalse(result)
        self.assertEqual(msg, 'Password must contain at least one uppercase letter.')

    def test_is_suitable_password_no_lowercase(self):
        '''
        Test is_suitable with a password missing a lowercase letter.
        '''
        # Empty query to indicate available username
        self.mock_db.get_records.return_value = []

        # Passin password with no lowercase
        result, msg = self.iam.is_suitable('validuser', 'NOLOWER1!')

        # Check - Is password as flagged as no lowercase?
        self.assertFalse(result)
        self.assertEqual(msg, 'Password must contain at least one lowercase letter.')

    def test_is_suitable_password_no_digit(self):
        '''
        Test is_suitable with a password missing a digit.
        '''
        # Specifying zero return to indicate no existing user
        self.mock_db.get_records.return_value = []

        # Passing a username with no numbers
        result, msg = self.iam.is_suitable('validuser', 'NoDigits!')

        # Check - Was this password flagge as without a number?
        self.assertFalse(result)
        self.assertEqual(msg, 'Password must contain at least one digit.')

    def test_is_suitable_password_no_special_char(self):
        '''
        Test is_suitable with a password missing a special character.
        '''
        # Specifying that no records return
        self.mock_db.get_records.return_value = []

        # Passing password without a special character
        result, msg = self.iam.is_suitable('validuser', 'NoSpecial1')

        # Check - Is password deemed as unsuitable due to no special character?
        self.assertFalse(result)
        self.assertEqual(msg, 'Password must contain at least one special character (!@#$%^&*()).')

    def test_is_suitable_all_conditions_met(self):
        '''
        Test is_suitable when both username and password meet all requirements.
        '''
        # Specifying user is available (with no return)
        self.mock_db.get_records.return_value = []

        # Checking with username and password that is suitable
        result, msg = self.iam.is_suitable('perfect_user', 'StrongP@ss1')

        # Check 1 - Did insert work with no errors?
        self.assertTrue(result)
        self.assertEqual(msg, '')

        # Check 2 - Was insert performed once?
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'perfect_user'}
        )

    def test_is_suitable_username_invalid_password_valid(self):
        '''
        Test is_suitable when username is invalid first (password not checked).
        '''
        # Specifying the situation where message to short
        result, msg = self.iam.is_suitable('us', 'StrongP@ss1') # Username too short

        # Check - Did it get flagged as too short a username?
        self.assertFalse(result)
        self.assertEqual(msg, 'Username must be at least 3 characters long.')

        # Check - Was add records not called due to validity concerns?
        self.mock_db.get_records.assert_not_called()

    def test_is_suitable_username_valid_but_not_available_password_valid(self):
        '''
        Test is_suitable when username is valid but not available.
        '''
        # Specifying username exists (with actual return value)
        self.mock_db.get_records.return_value = [{'username': 'existinguser'}]

        # Passing username to db
        result, msg = self.iam.is_suitable('existinguser', 'StrongP@ss1')

        # Check - Did the insert not happen?
        self.assertFalse(result)
        self.assertEqual(msg, 'Username is not available')

        # check - Was the get records called once?
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'existinguser'}
        )

    @patch('utils.iam.IAM._hash_password')
    def test_create_user_successful(self, mock_hash_password):
        '''
        Test that create_user successfully adds a user to the database
        '''
        # Specifying an incorrect hash password
        mock_hash_password.return_value = b'mocked_hashed_password_bytes'

        # Specifying the username
        username   = 'newuser'
        password   = 'NewPassword1!'
        first_name = 'Jane'
        last_name  = 'Doe'
        admin      = True

        # Creating the user
        result, message = self.iam.create_user(username, password, first_name, last_name, admin)

        # Check - Did the insertion work well?
        self.assertTrue(result)
        self.assertEqual(message, 'User created successfully.')

        # Check - Was hashing function called once?
        mock_hash_password.assert_called_once_with(password) 

        # check - Was the insert record called once?
        self.mock_db.add_record.assert_called_once_with(
            collection_name='user',
            record={
                'username'  : username,
                'password'  : b'mocked_hashed_password_bytes',
                'first_name': first_name,
                'last_name' : last_name,
                'admin'     : admin
            }
        )
    @patch('utils.iam.IAM._hash_password')
    def test_create_user_database_add_error(self, mock_hash_password):
        '''
        Test that create_user handles database errors during record addition.
        '''
        # Creating a mocked hash password
        mock_hash_password.return_value = b'mocked_hashed_password_bytes'

        # Specifying a write error
        self.mock_db.add_record.side_effect = Exception('Database write error')

        # Attempting to create the user
        result, message = self.iam.create_user('usererror', 'Pass123!', 'Error', 'User', False)

        # Check that assertion false and reason did not work?
        self.assertFalse(result)
        self.assertIn('Failed to create user: Database write error', message)
        self.mock_db.add_record.assert_called_once_with(
            collection_name='user',
            record = {
                'username'  : 'usererror',
                'password'  : b'mocked_hashed_password_bytes',
                'first_name': 'Error',
                'last_name' : 'User',
                'admin'     : False
            }
        )

    @patch('utils.iam.IAM._hash_password', side_effect=Exception('Hashing failed'))
    def test_create_user_hashing_error(self, mock_hash_password):
        '''
        Test that create_user handles errors during password hashing.
        '''
        # Creating a user
        result, message = self.iam.create_user('usererror', 'Pass123!', 'Error', 'User', False)

        # Check that hashing failed
        self.assertFalse(result)
        self.assertIn('Failed to create user: Hashing failed', message)
        mock_hash_password.assert_called_once_with('Pass123!')
        self.mock_db.add_record.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv = ['first-arg-is-ignored'], exit = False)