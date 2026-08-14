import unittest

from app.utils.user import User

class TestUser(unittest.TestCase):
    '''
    Unit testing that statically tests
    the user class
    '''
    def setUp(self):
        '''
        Sets up the user object
        ready for testing
        '''
        # User 1 - Regular lvel user
        self.regular_user = User(
            username   = 'john.doe',
            first_name = 'John',
            last_name  = 'Doe',
            admin      = False
        )
        # User 2 - Admin user
        self.admin_user = User(
            username   = 'admin.smith',
            first_name = 'Alice',
            last_name = 'Smith',
            admin     = True
        )
        # User 3 - A default user (admin goes to fault)
        self.default_admin_user = User(
            username   = 'default.user',
            first_name = 'Dave',
            last_name  = 'Jones' 
        )
    def test_user_initialization_regular_user(self):
        '''
        Performs a check on the user 1 to ensure all the 
        attributes are correctly set
        '''
        # Performing the checks
        self.assertEqual(self.regular_user.__username__, 'john.doe')
        self.assertEqual(self.regular_user.__first_name__, 'John')
        self.assertEqual(self.regular_user.__last_name__, 'Doe')
        self.assertFalse(self.regular_user.__admin__)

    def test_user_initialization_admin_user(self):
        '''
        Performs a check of user 2 to ensure that all
        the attributes are correct for user 2 (the admin)
        '''
        # Performs the checks
        self.assertEqual(self.admin_user.__username__, 'admin.smith')
        self.assertEqual(self.admin_user.__first_name__, 'Alice')
        self.assertEqual(self.admin_user.__last_name__, 'Smith')
        self.assertTrue(self.admin_user.__admin__)

    def test_user_initialization_default_admin_false(self):
        '''
        Performs a check of user 3 to ensure the attributes
        are set correct for user 3, where defaults are left
        '''
        # Perform the checks
        self.assertEqual(self.default_admin_user.__username__, 'default.user')
        self.assertFalse(self.default_admin_user.__admin__)


    def test_user_initialization_with_empty_strings(self):
        '''
        Test initialization with empty strings for names
        '''
        # Setting up an empty user
        empty_user = User("", "", "", False)

        # Checking imports are valid and 
        self.assertEqual(empty_user.__username__, "")
        self.assertEqual(empty_user.__first_name__, "")
        self.assertEqual(empty_user.__last_name__, "")
        self.assertFalse(empty_user.__admin__)

    def test_str_representation_regular_user(self):
        '''
        Test the string representation for a regular user.
        '''
        # Creating the string representation separately
        expected_str = 'User (user) - john.doe: John Doe'

        # Checking the user's string representation is the same
        self.assertEqual(str(self.regular_user), expected_str)

    def test_str_representation_admin_user(self):
        '''
        Test the string representation for an admin user.
        '''
        # Expected representation of admin user
        expected_str = 'User (admin) - admin.smith: Alice Smith'

        # Checking admin user representation
        self.assertEqual(str(self.admin_user), expected_str)


    def test_repr_representation_regular_user(self):
        '''
        Test the representation string for a regular user.
        '''
        # Retrieving representation of regular user (user 3)
        expected_repr = "User (User (user) - john.doe: John Doe)"

        # Checking string for user 3
        self.assertEqual(repr(self.regular_user), expected_repr)

    def test_repr_representation_admin_user(self):
        '''
        Test the representation string for an admin user
        '''
        # Checking rep string
        expected_repr = "User (User (admin) - admin.smith: Alice Smith)"
        self.assertEqual(repr(self.admin_user), expected_repr)

    def test_is_admin_true_for_admin_user(self):
        '''
        Test is_admin returns True for an admin user.
        '''
        # Checking admin status of user one
        self.assertTrue(self.admin_user.is_admin())

    def test_is_admin_false_for_regular_user(self):
        '''
        Test is_admin returns False for a regular user
        '''
        # Checking admin status of user 2
        self.assertFalse(self.regular_user.is_admin())

    def test_is_admin_false_for_default_admin_user(self):
        '''
        Test is_admin returns False for a user with default admin status.
        '''
        # Checking admin status of default user
        self.assertFalse(self.default_admin_user.is_admin())

    def test_get_username(self):
        '''
        Test that get_username returns the correct username.
        '''
        # Retrieving and checking user of two users
        self.assertEqual(self.regular_user.get_username(), "john.doe")
        self.assertEqual(self.admin_user.get_username(), "admin.smith")

    def test_get_name_regular_user(self):
        '''
        Test that get_name returns the full name for a regular user
        '''
        # Retrieving and checking full name repesentation
        self.assertEqual(self.regular_user.get_name(), "John Doe")

    def test_get_name_admin_user(self):
        '''
        Test that get_name returns the full name for an admin user
        '''
        # Checking full name representation
        self.assertEqual(self.admin_user.get_name(), "Alice Smith")

    def test_get_name_with_empty_names(self):
        '''
        Test get_name with empty first and last names
        '''
        # Creating a blank user
        empty_name_user = User("test", "", "", False)

        # Checking an empty use strin representation
        self.assertEqual(empty_name_user.get_name(), " ") 

    # --- Test cases for to_dict ---
    def test_to_dict_regular_user(self):
        '''
        Test that to_dict returns the correct dictionary for a regular user
        '''
        # Dictionary we would expected from user 1
        expected_dict = {
            'username': 'john.doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'admin': False
        }
        # Performing a check of user 1
        self.assertEqual(self.regular_user.to_dict(), expected_dict)

    def test_to_dict_admin_user(self):
        '''
        Test that to_dict returns the correct dictionary for an admin user
        '''
        # Expected dictionary of user 2 (admin)
        expected_dict = {
            'username': 'admin.smith',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'admin': True
        }
        # Performing check of admin user
        self.assertEqual(self.admin_user.to_dict(), expected_dict)

    def test_to_dict_default_admin_user(self):
        '''
        Test that to_dict returns the correct dictionary for a user with default admin status
        '''
        # Expected dict of default user (user 3)
        expected_dict = {
            'username': 'default.user',
            'first_name': 'Dave',
            'last_name': 'Jones',
            'admin': False
        }
        # Performing comparison of default user
        self.assertEqual(self.default_admin_user.to_dict(), expected_dict)

    def test_to_dict_with_empty_strings(self):
        '''
        Test to_dict with empty strings for user attributes
        '''
        # Creating an empty user
        empty_str_user = User(username = "", first_name = "", last_name = "", admin = False)
        
        # Creating an empty user dict
        expected_dict = {
            'username': '',
            'first_name': '',
            'last_name': '',
            'admin': False
        }
        # Checking the empty user equality
        self.assertEqual(empty_str_user.to_dict(), expected_dict)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)