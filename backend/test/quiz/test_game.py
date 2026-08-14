# backend/test/utils/test_api.py

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# --- CRUCIAL SYS.PATH MODIFICATION ---
# Get the absolute path of the current test file's directory (backend/test/utils)
current_test_dir = os.path.dirname(os.path.abspath(__file__))
# Get the path to the 'backend' root directory (three levels up from test/utils)
# current_test_dir -> 'backend/test/utils'
# os.path.dirname(current_test_dir) -> 'backend/test'
# os.path.dirname(os.path.dirname(current_test_dir)) -> 'backend/'
backend_root_dir = os.path.dirname(os.path.dirname(current_test_dir))
# Add 'backend/' to sys.path so Python can find 'backend.utils.api', etc.
sys.path.insert(0, backend_root_dir)
# --- END SYS.PATH MODIFICATION ---

# Now, imports should work relative to the 'backend' root
# For 'api.py' which is now at backend/utils/api.py
from backend.utils.api import router # Correct import based on its actual location
from backend.utils.api import get_iam # Correct import based on its actual location

# For IAM and User classes, also from backend/utils/
from backend.utils.iam import IAM
from backend.utils.user import User

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.security import OAuth2PasswordRequestForm # For mocking form_data

# Create a FastAPI app instance for testing
app = FastAPI()
# Include the router from your api.py (which is now in utils/)
app.include_router(router)


class TestAPI(unittest.TestCase):
    '''
    Unit tests for the FastAPI API endpoints.
    These tests use TestClient and mock dependencies.
    '''

    def setUp(self):
        '''Set up the test client and mock IAM for each test.'''
        self.mock_iam = MagicMock(spec = IAM)
        # Apply dependency override for the current test client
        # This tells FastAPI to use our mock_iam whenever get_iam is requested
        app.dependency_overrides[get_iam] = lambda: self.mock_iam
        self.client = TestClient(app)

        # Common user data for mocks
        self.test_user_data = {
            'username': 'testuser',
            'password': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User',
            'admin': False
        }
        self.mock_user_obj = User(
            username = 'testuser', first_name = 'Test', last_name = 'User', admin = False
        )

    def tearDown(self):
        '''Clean up dependency overrides after each test.'''
        app.dependency_overrides.clear() # Clear overrides to avoid affecting other tests

    # --- Test Cases for /token (Login) ---

    def test_login_success(self):
        '''Test successful user login.'''
        # Configure mock IAM behavior
        self.mock_iam.check_user.return_value = True
        self.mock_iam.get_user.return_value = self.mock_user_obj

        response = self.client.post(
            '/token',
            data = {'username': 'testuser', 'password': 'correctpassword'},
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'access_token': 'testuser', 'token_type': 'bearer'})
        self.mock_iam.check_user.assert_called_once_with(username = 'testuser', password = 'correctpassword')
        self.mock_iam.get_user.assert_called_once_with(username = 'testuser')

    def test_login_incorrect_credentials(self):
        '''Test login with incorrect username or password.'''
        # Simulate incorrect credentials
        self.mock_iam.check_user.return_value = False

        response = self.client.post(
            '/token',
            data = {'username': 'wronguser', 'password': 'wrongpassword'},
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Incorrect username or password'})
        self.mock_iam.check_user.assert_called_once_with(username = 'wronguser', password = 'wrongpassword')
        # get_user should not be called if check_user fails
        self.mock_iam.get_user.assert_not_called()

    def test_login_iam_get_user_fails_after_check(self):
        '''Test internal server error if get_user fails after check_user passes.'''
        self.mock_iam.check_user.return_value = True
        # Simulate get_user failure (e.g., DB error after check)
        self.mock_iam.get_user.return_value = None

        response = self.client.post(
            '/token',
            data = {'username': 'testuser', 'password': 'correctpassword'},
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'User found during verification but not during login. Internal error.'})
        self.mock_iam.check_user.assert_called_once()
        self.mock_iam.get_user.assert_called_once()

    # --- Test Cases for /register ---

    def test_register_success(self):
        '''Test successful user registration.'''
        # Simulate suitable username/password
        self.mock_iam.is_suitable.return_value = (True, '')
        # Simulate successful creation
        self.mock_iam.create_user.return_value = (True, 'User created successfully.')
        self.mock_iam.get_user.return_value = self.mock_user_obj # User retrieval success

        response = self.client.post(
            '/register',
            json = self.test_user_data
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'username': 'testuser',
            'admin': False,
            'full_name': 'Test User',
            'last_name': 'User'
        })
        self.mock_iam.is_suitable.assert_called_once_with(self.test_user_data['username'], self.test_user_data['password'])
        self.mock_iam.create_user.assert_called_once_with(
            username = self.test_user_data['username'],
            password = self.test_user_data['password'],
            first_name = self.test_user_data['first_name'],
            last_name = self.test_user_data['last_name'],
            admin = self.test_user_data['admin']
        )
        self.mock_iam.get_user.assert_called_once_with(self.test_user_data['username'])


    def test_register_invalid_data_unsuitable_username(self):
        '''Test registration with unsuitable username/password from IAM.is_suitable.'''
        # Simulate unsuitable
        self.mock_iam.is_suitable.return_value = (False, 'Username too short.')

        response = self.client.post(
            '/register',
            json = {**self.test_user_data, 'username': 'ab'} # Override username to be too short
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Username too short.'})
        self.mock_iam.is_suitable.assert_called_once_with('ab', self.test_user_data['password'])
        self.mock_iam.create_user.assert_not_called()
        self.mock_iam.get_user.assert_not_called()

    def test_register_iam_create_user_fails(self):
        '''Test internal server error if IAM.create_user explicitly fails.'''
        self.mock_iam.is_suitable.return_value = (True, '') # Suitable
        self.mock_iam.create_user.return_value = (False, 'Database write error.') # Creation fails

        response = self.client.post(
            '/register',
            json = self.test_user_data
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'Registration failed: Database write error.'})
        self.mock_iam.is_suitable.assert_called_once()
        self.mock_iam.create_user.assert_called_once()
        self.mock_iam.get_user.assert_not_called()

    def test_register_iam_get_user_fails_after_create(self):
        '''Test internal server error if get_user fails after successful creation.'''
        self.mock_iam.is_suitable.return_value = (True, '')
        self.mock_iam.create_user.return_value = (True, 'User created successfully.')
        self.mock_iam.get_user.return_value = None # Retrieval fails

        response = self.client.post(
            '/register',
            json = self.test_user_data
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'User registered but could not be retrieved post-registration. Internal error.'})
        self.mock_iam.is_suitable.assert_called_once()
        self.mock_iam.create_user.assert_called_once()
        self.mock_iam.get_user.assert_called_once()

    # --- Test Cases for Protected Endpoints (using get_current_user dependency) ---

    def test_get_current_user_success(self):
        '''Test successful retrieval of current user via /users/me.'''
        self.mock_iam.get_user.return_value = self.mock_user_obj

        response = self.client.get(
            '/users/me',
            headers = {'Authorization': 'Bearer testuser'} # Simulate token
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'username': 'testuser',
            'admin': False,
            'full_name': 'Test User',
            'last_name': 'User'
        })
        self.mock_iam.get_user.assert_called_once_with(username = 'testuser')

    def test_get_current_user_invalid_token(self):
        '''Test handling of invalid token (get_user returns None) for protected endpoint.'''
        self.mock_iam.get_user.return_value = None # Simulate user not found for token

        response = self.client.get(
            '/users/me',
            headers = {'Authorization': 'Bearer invalid_token'}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Could not validate credentials'})
        self.mock_iam.get_user.assert_called_once_with(username = 'invalid_token')

    def test_get_protected_data_success(self):
        '''Test accessing protected data with a valid token.'''
        self.mock_iam.get_user.return_value = self.mock_user_obj

        response = self.client.get(
            '/protected_data',
            headers = {'Authorization': 'Bearer testuser'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Hello, testuser! This is protected data.'})
        self.mock_iam.get_user.assert_called_once_with(username = 'testuser')


if __name__ == '__main__':
    unittest.main()