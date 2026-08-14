import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# API that is under test
from app.utils.api import router # Correct import based on its actual location
from app.utils.api import get_iam # Correct import based on its actual location

# Important classes that need to be
from app.utils.iam import IAM
from app.utils.user import User

# Fast API functionality (as that is how app interacts)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.security import OAuth2PasswordRequestForm # For mocking form_data

# Create a FastAPI app instance for testing
app = FastAPI()\

# Include the router from your api
app.include_router(router)


class TestAPI(unittest.TestCase):
    '''
    Unit tests for the FastAPI API endpoints.
    These tests use TestClient and mock dependencies.
    '''

    def setUp(self):
        '''
        Set up the test client and mock IAM for each test.
        '''
        # Create a mock interface 
        self.mock_iam = MagicMock(spec = IAM)

        # Apply dependency override for the current test client
        app.dependency_overrides[get_iam] = lambda: self.mock_iam
        self.client = TestClient(app)

        # What is returned from user data
        self.test_user_data = {
            'username'   : 'testuser',
            'password'   : 'Password123!',
            'first_name' : 'Test',
            'last_name'  : 'User',
            'admin'      : False
        }
        # Use the updated User class
        self.mock_user_obj = User(
            username = 'testuser', first_name = 'Test', last_name = 'User', admin = False
        )

    def tearDown(self):
        '''
        Clean up dependency overrides after each test.
        '''
        app.dependency_overrides.clear() 

    def test_login_success(self):
        '''
        Test successful user login.
        '''
        # Configure mock IAM behavior
        self.mock_iam.check_user.return_value = True
        self.mock_iam.get_user.return_value = self.mock_user_obj

        # Simulating the response
        response = self.client.post(
            '/token',
            data = {'username': 'testuser', 'password': 'correctpassword'},
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        )
        # Check - Has correct information been returned?
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'access_token': 'testuser', 'token_type': 'bearer'})
        
        # Check - Have the two methods only been called once?
        self.mock_iam.check_user.assert_called_once_with(username = 'testuser', password = 'correctpassword')
        self.mock_iam.get_user.assert_called_once_with(username = 'testuser')

    def test_login_incorrect_credentials(self):
        '''
        Test login with incorrect username or password.
        '''
        # Simulate incorrect credentials
        self.mock_iam.check_user.return_value = False

        # Posting the client
        response = self.client.post(
            '/token',
            data = {'username': 'wronguser', 'password': 'wrongpassword'},
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        )
        # Check - Has incorrect username and password been identified?
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Incorrect username or password'})

        # Check - Has the get user method been called once?
        self.mock_iam.check_user.assert_called_once_with(username = 'wronguser', password = 'wrongpassword')
        
        # Check - Has get user not been called?
        self.mock_iam.get_user.assert_not_called()

    def test_login_iam_get_user_fails_after_check(self):
        '''
        Test internal server error if get_user fails after check_user passes.
        '''
        # Specifying that the suitability of user is true
        self.mock_iam.check_user.return_value = True

        # Simulate get_user failure (e.g., DB error after check)
        self.mock_iam.get_user.return_value = None

        # Response from app
        response = self.client.post(
            '/token',
            data = {'username': 'testuser', 'password': 'correctpassword'},
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        )

        # Check - Internal service error
        self.assertEqual(response.status_code, 500)

        # Check - Database error
        self.assertEqual(response.json(), {'detail': 'User found during verification but not during login. Internal error.'})
        
        # Check - both check and get only called once
        self.mock_iam.check_user.assert_called_once()
        self.mock_iam.get_user.assert_called_once()

    def test_register_success(self):
        '''
        Test successful user registration.
        '''

        # Simulate suitable username/password
        self.mock_iam.is_suitable.return_value = (True, '')

        # Simulate successful creation
        self.mock_iam.create_user.return_value = (True, 'User created successfully.')
        self.mock_iam.get_user.return_value = self.mock_user_obj # User retrieval success

        # Replication the response
        response = self.client.post(
            '/register',
            json = self.test_user_data
        )
        # Checking correct codes and response
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'username' : 'testuser',
            'admin'    : False,
            'full_name': 'Test User',
            'last_name': 'User'
        })
        # Check - Suitable username only called once
        self.mock_iam.is_suitable.assert_called_once_with(self.test_user_data['username'], self.test_user_data['password'])
        
        # Check - Creation of user profile done properly
        self.mock_iam.create_user.assert_called_once_with(
            username = self.test_user_data['username'],
            password = self.test_user_data['password'],
            first_name = self.test_user_data['first_name'],
            last_name = self.test_user_data['last_name'],
            admin = self.test_user_data['admin']
        )
        self.mock_iam.get_user.assert_called_once_with(self.test_user_data['username'])


    def test_register_invalid_data_unsuitable_username(self):
        '''
        Test registration with unsuitable username/password from IAM.is_suitable.
        '''
        # Simulate unsuitable values of username
        self.mock_iam.is_suitable.return_value = (False, 'Username too short.')

        # Posting the response
        response = self.client.post(
            '/register',
            json = {**self.test_user_data, 'username': 'ab'} 
        )
        # Check appropriate error codes for incorrect username
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Username too short.'})

        # Check was is-suitable called and create / get not
        self.mock_iam.is_suitable.assert_called_once_with('ab', self.test_user_data['password'])
        self.mock_iam.create_user.assert_not_called()
        self.mock_iam.get_user.assert_not_called()

    def test_register_iam_create_user_fails(self):
        '''
        Test internal server error if IAM.create_user explicitly fails.
        '''
        # Specifying the return of suitable is true but create goes wrong
        self.mock_iam.is_suitable.return_value = (True, '') 
        self.mock_iam.create_user.return_value = (False, 'Database write error.') 

        # Passing the response from API
        response = self.client.post(
            '/register',
            json = self.test_user_data
        )
        # Checking the error codes and messages
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'Registration failed: Database write error.'})
        
        # Checking is_suitable and create executed but went wrong after get
        self.mock_iam.is_suitable.assert_called_once()
        self.mock_iam.create_user.assert_called_once()
        self.mock_iam.get_user.assert_not_called()

    def test_register_iam_get_user_fails_after_create(self):
        '''
        Test internal server error if get_user fails after successful creation.
        '''
        # Specifying a suitable user and creation but can't get user
        self.mock_iam.is_suitable.return_value = (True, '')
        self.mock_iam.create_user.return_value = (True, 'User created successfully.')
        self.mock_iam.get_user.return_value    = None 

        # The response
        response = self.client.post(
            '/register',
            json = self.test_user_data
        )
        # Check correct status code and error message
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'User registered but could not be retrieved post-registration. Internal error.'})
        
        # Checking all methods executed once
        self.mock_iam.is_suitable.assert_called_once()
        self.mock_iam.create_user.assert_called_once()
        self.mock_iam.get_user.assert_called_once()

    def test_get_current_user_success(self):
        '''
        Test successful retrieval of current user via /users/me.
        '''
        # Specifying a correct user profile
        self.mock_iam.get_user.return_value = self.mock_user_obj

        # Retrieving the user
        response = self.client.get(
            '/users/me',
            headers = {'Authorization': 'Bearer testuser'} # Simulate token
        )
        # Checking successful return and user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'username' : 'testuser',
            'admin'    : False,
            'full_name': 'Test User',
            'last_name': 'User'
        })
        self.mock_iam.get_user.assert_called_once_with(username = 'testuser')

    def test_get_current_user_invalid_token(self):
        '''
        Test handling of invalid token (get_user returns None) for protected endpoint.
        '''
        # Simulate user not found for token
        self.mock_iam.get_user.return_value = None 

        # Retrieving a client response
        response = self.client.get(
            '/users/me',
            headers = {'Authorization': 'Bearer invalid_token'}
        )
        # Check unauthorised credentials
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Could not validate credentials'})

        # Check - get method only called once
        self.mock_iam.get_user.assert_called_once_with(username = 'invalid_token')

    def test_get_protected_data_success(self):
        '''
        Test accessing protected data with a valid token.
        '''
        # Specifying method will return user
        self.mock_iam.get_user.return_value = self.mock_user_obj

        # Response from IAM
        response = self.client.get(
            '/protected_data',
            headers = {'Authorization': 'Bearer testuser'}
        )
        # checking correct response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Hello, testuser! This is protected data.'})
        
        # Check - Was get called only once?
        self.mock_iam.get_user.assert_called_once_with(username = 'testuser')


if __name__ == '__main__':
    unittest.main()