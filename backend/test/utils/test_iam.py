import unittest
from unittest.mock import MagicMock, patch
import bcrypt
import re

from app.utils.iam import IAM

from app.utils.user import User

class TestIAM(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.iam     = IAM(db = self.mock_db)

        self.known_password = 'TestPass1!'
        self.known_hashed_password_bytes = bcrypt.hashpw(self.known_password.encode('utf-8'), bcrypt.gensalt())

        self.mock_user_data = {
            'username'   : 'existinguser',
            'password'   : self.known_hashed_password_bytes,
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
        self.assertIs(self.iam.db, self.mock_db)

        self.assertEqual(self.iam.db_collection, 'user')

    @patch('utils.iam.IAM._hash_password')
    def test_hash_password_returns_consistent_hash_with_fixed_salt(self, mock_hash_password):
        mock_hash_password.return_value = bcrypt.hashpw(b'some_password_to_hash', bcrypt.gensalt())

        password = 'mysecretpassword'
        hashed_password = self.iam._hash_password(password)

        self.assertIsInstance(hashed_password, bytes)

        self.assertTrue(len(hashed_password) > 0)

        mock_hash_password.assert_called_once_with(password)

    def test_check_hashed_password_correct_password(self):
        self.assertTrue(self.iam._check_hashed_password(self.known_password, self.known_hashed_password_bytes))

    def test_check_hashed_password_incorrect_password(self):
        self.assertFalse(self.iam._check_hashed_password('WrongPass1!', self.known_hashed_password_bytes))

    def test_check_hashed_password_empty_password(self):
        self.assertFalse(self.iam._check_hashed_password('', self.known_hashed_password_bytes))

    def test_check_hashed_password_empty_hashed_password_bytes(self):
        with self.assertRaises(ValueError, msg = 'bcrypt.checkpw should raise ValueError for empty hash'):
            self.iam._check_hashed_password(self.known_password, b'')

    def test_check_hashed_password_malformed_hashed_password(self):
        with self.assertRaises(ValueError, msg = 'bcrypt.checkpw should raise ValueError for malformed hash'):
            self.iam._check_hashed_password(self.known_password, b'invalid_hash_string')

    def test_check_user_valid_username_correct_password(self):
        self.mock_db.get_records.return_value = [self.mock_user_data]

        self.assertTrue(self.iam.check_user('existinguser', self.known_password))
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'existinguser'}
        )

    def test_check_user_valid_username_incorrect_password(self):
        self.mock_db.get_records.return_value = [self.mock_user_data]

        self.assertFalse(self.iam.check_user('existinguser', 'WrongPass1!'))
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'existinguser'}
        )

    def test_check_user_username_not_found(self):
        self.mock_db.get_records.return_value = []
        self.assertFalse(self.iam.check_user('nonexistentuser', 'anypassword'))
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'nonexistentuser'}
        )

    def test_check_user_empty_username(self):
        self.mock_db.get_records.return_value = []

        self.assertFalse(self.iam.check_user('', 'anypassword'))
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': ''}
        )

    def test_check_user_empty_password(self):
        self.mock_db.get_records.return_value = [self.mock_user_data]

        self.assertFalse(self.iam.check_user('existinguser', ''))
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'existinguser'}
        )

    def test_check_user_database_error_on_get_records(self):
        self.mock_db.get_records.side_effect = Exception('Database connection lost')

        self.assertFalse(self.iam.check_user('testuser', self.known_password))
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'testuser'}
        )

    @patch('utils.iam.IAM._check_hashed_password')
    def test_check_user_password_as_string_in_db(self, mock_check_hashed_password):
        mock_check_hashed_password.return_value = True

        user_data_str_password = self.mock_user_data.copy()
        user_data_str_password['password'] = self.known_hashed_password_bytes.decode('utf-8')

        self.mock_db.get_records.return_value = [user_data_str_password]
        self.assertTrue(self.iam.check_user('existinguser', self.known_password))

        mock_check_hashed_password.assert_called_once_with(
            self.known_password, user_data_str_password['password'].encode('utf-8')
        )
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'existinguser'}
        )

    def test_get_user_existing_username_returns_user_object(self):
        self.mock_db.get_records.return_value = [self.mock_user_data]
        user_profile = self.iam.get_user('existinguser')

        self.assertIsInstance(user_profile, User)
        self.assertEqual(user_profile.get_username(), self.mock_user_data['username'])
        self.assertEqual(user_profile.to_dict()['first_name'], self.mock_user_data['first_name'])
        self.assertEqual(user_profile.to_dict()['last_name'], self.mock_user_data['last_name'])
        self.assertEqual(user_profile.is_admin(), self.mock_user_data['admin'])

        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'existinguser'}
        )

    def test_get_user_admin_user(self):
        self.mock_db.get_records.return_value = [self.mock_admin_user_data]
        user_profile = self.iam.get_user('adminuser')

        self.assertTrue(user_profile.is_admin())
        self.assertEqual(user_profile.get_username(), self.mock_admin_user_data['username'])
        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'adminuser'}
        )

    def test_get_user_non_existent_username_returns_none(self):
        self.mock_db.get_records.return_value = []
        user_profile = self.iam.get_user('nonexistent')

        self.assertIsNone(user_profile)
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'nonexistent'}
        )

    def test_get_user_database_error_returns_none(self):
        self.mock_db.get_records.side_effect = Exception('DB read error')

        self.assertIsNone(self.iam.get_user('anyuser'))
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'anyuser'}
        )

    def test_get_user_incomplete_data_from_db_missing_key(self):
        incomplete_user_data = {
            'username'  : 'incomplete',
            'password'  : b'some_hash',
            'first_name': 'Incomplete',
            'admin'     : False
        }
        self.mock_db.get_records.return_value = [incomplete_user_data]

        user_profile = self.iam.get_user('incomplete')

        self.assertIsInstance(user_profile, User)
        self.assertEqual(user_profile.get_username(), 'incomplete')
        self.assertIsNone(user_profile.to_dict()['last_name'])
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'incomplete'}
        )

    def test_is_suitable_username_too_short(self):
        result, msg = self.iam.is_suitable('ab', 'ValidPass1!')

        self.assertFalse(result)
        self.assertEqual(msg, 'Username must be at least 3 characters long.')
        self.mock_db.get_records.assert_not_called()

    def test_is_suitable_username_invalid_characters(self):
        result, msg = self.iam.is_suitable('user-name', 'ValidPass1!')

        self.assertFalse(result)
        self.assertEqual(msg, 'Username can only contain alphanumeric characters and underscores.')
        self.mock_db.get_records.assert_not_called()

    def test_is_suitable_username_not_available(self):
        self.mock_db.get_records.return_value = [{'username': 'existinguser'}]
        result, msg = self.iam.is_suitable('existinguser', 'ValidPass1!')

        self.assertFalse(result)
        self.assertEqual(msg, 'Username is not available')
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'existinguser'}
        )

    def test_is_suitable_username_available_and_valid(self):
        self.mock_db.get_records.return_value = []
        result, msg = self.iam.is_suitable('new_valid_user', 'ValidPass1!')

        self.assertTrue(result)
        self.assertEqual(msg, '')
        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'new_valid_user'}
        )

    def test_is_suitable_database_error_on_uniqueness_check(self):
        self.mock_db.get_records.side_effect = Exception('DB connection down')

        result, msg = self.iam.is_suitable('anyuser', 'ValidPass1!')
        self.assertFalse(result)
        self.assertEqual(msg, 'Error checking username availability.')

        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'anyuser'}
        )

    def test_is_suitable_password_too_short(self):
        self.mock_db.get_records.return_value = []

        result, msg = self.iam.is_suitable('validuser', 'Short1!')

        self.assertFalse(result)
        self.assertEqual(msg, 'Password must be at least 8 characters long.')

    def test_is_suitable_password_no_uppercase(self):
        self.mock_db.get_records.return_value = []

        result, msg = self.iam.is_suitable('validuser', 'noupper1!')

        self.assertFalse(result)
        self.assertEqual(msg, 'Password must contain at least one uppercase letter.')

    def test_is_suitable_password_no_lowercase(self):
        self.mock_db.get_records.return_value = []

        result, msg = self.iam.is_suitable('validuser', 'NOLOWER1!')

        self.assertFalse(result)
        self.assertEqual(msg, 'Password must contain at least one lowercase letter.')

    def test_is_suitable_password_no_digit(self):
        self.mock_db.get_records.return_value = []

        result, msg = self.iam.is_suitable('validuser', 'NoDigits!')

        self.assertFalse(result)
        self.assertEqual(msg, 'Password must contain at least one digit.')

    def test_is_suitable_password_no_special_char(self):
        self.mock_db.get_records.return_value = []

        result, msg = self.iam.is_suitable('validuser', 'NoSpecial1')

        self.assertFalse(result)
        self.assertEqual(msg, 'Password must contain at least one special character (!@#$%^&*()).')

    def test_is_suitable_all_conditions_met(self):
        self.mock_db.get_records.return_value = []

        result, msg = self.iam.is_suitable('perfect_user', 'StrongP@ss1')

        self.assertTrue(result)
        self.assertEqual(msg, '')

        self.mock_db.get_records.assert_called_once_with(
            collection_name = 'user', query = {'username': 'perfect_user'}
        )

    def test_is_suitable_username_invalid_password_valid(self):
        result, msg = self.iam.is_suitable('us', 'StrongP@ss1')

        self.assertFalse(result)
        self.assertEqual(msg, 'Username must be at least 3 characters long.')

        self.mock_db.get_records.assert_not_called()

    def test_is_suitable_username_valid_but_not_available_password_valid(self):
        self.mock_db.get_records.return_value = [{'username': 'existinguser'}]

        result, msg = self.iam.is_suitable('existinguser', 'StrongP@ss1')

        self.assertFalse(result)
        self.assertEqual(msg, 'Username is not available')

        self.mock_db.get_records.assert_called_once_with(
            collection_name='user', query={'username': 'existinguser'}
        )

    @patch('utils.iam.IAM._hash_password')
    def test_create_user_successful(self, mock_hash_password):
        mock_hash_password.return_value = b'mocked_hashed_password_bytes'

        username   = 'newuser'
        password   = 'NewPassword1!'
        first_name = 'Jane'
        last_name  = 'Doe'
        admin      = True

        result, message = self.iam.create_user(username, password, first_name, last_name, admin)

        self.assertTrue(result)
        self.assertEqual(message, 'User created successfully.')

        mock_hash_password.assert_called_once_with(password)

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
        mock_hash_password.return_value = b'mocked_hashed_password_bytes'

        self.mock_db.add_record.side_effect = Exception('Database write error')

        result, message = self.iam.create_user('usererror', 'Pass123!', 'Error', 'User', False)

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
        result, message = self.iam.create_user('usererror', 'Pass123!', 'Error', 'User', False)

        self.assertFalse(result)
        self.assertIn('Failed to create user: Hashing failed', message)
        mock_hash_password.assert_called_once_with('Pass123!')
        self.mock_db.add_record.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv = ['first-arg-is-ignored'], exit = False)