import unittest

from app.utils.user import User

class TestUser(unittest.TestCase):
    def setUp(self):
        self.regular_user = User(
            username   = 'john.doe',
            first_name = 'John',
            last_name  = 'Doe',
            admin      = False
        )
        self.admin_user = User(
            username   = 'admin.smith',
            first_name = 'Alice',
            last_name = 'Smith',
            admin     = True
        )
        self.default_admin_user = User(
            username   = 'default.user',
            first_name = 'Dave',
            last_name  = 'Jones'
        )
    def test_user_initialization_regular_user(self):
        self.assertEqual(self.regular_user.__username__, 'john.doe')
        self.assertEqual(self.regular_user.__first_name__, 'John')
        self.assertEqual(self.regular_user.__last_name__, 'Doe')
        self.assertFalse(self.regular_user.__admin__)

    def test_user_initialization_admin_user(self):
        self.assertEqual(self.admin_user.__username__, 'admin.smith')
        self.assertEqual(self.admin_user.__first_name__, 'Alice')
        self.assertEqual(self.admin_user.__last_name__, 'Smith')
        self.assertTrue(self.admin_user.__admin__)

    def test_user_initialization_default_admin_false(self):
        self.assertEqual(self.default_admin_user.__username__, 'default.user')
        self.assertFalse(self.default_admin_user.__admin__)


    def test_user_initialization_with_empty_strings(self):
        empty_user = User("", "", "", False)

        self.assertEqual(empty_user.__username__, "")
        self.assertEqual(empty_user.__first_name__, "")
        self.assertEqual(empty_user.__last_name__, "")
        self.assertFalse(empty_user.__admin__)

    def test_str_representation_regular_user(self):
        expected_str = 'User (user) - john.doe: John Doe'

        self.assertEqual(str(self.regular_user), expected_str)

    def test_str_representation_admin_user(self):
        expected_str = 'User (admin) - admin.smith: Alice Smith'

        self.assertEqual(str(self.admin_user), expected_str)


    def test_repr_representation_regular_user(self):
        expected_repr = "User (User (user) - john.doe: John Doe)"

        self.assertEqual(repr(self.regular_user), expected_repr)

    def test_repr_representation_admin_user(self):
        expected_repr = "User (User (admin) - admin.smith: Alice Smith)"
        self.assertEqual(repr(self.admin_user), expected_repr)

    def test_is_admin_true_for_admin_user(self):
        self.assertTrue(self.admin_user.is_admin())

    def test_is_admin_false_for_regular_user(self):
        self.assertFalse(self.regular_user.is_admin())

    def test_is_admin_false_for_default_admin_user(self):
        self.assertFalse(self.default_admin_user.is_admin())

    def test_get_username(self):
        self.assertEqual(self.regular_user.get_username(), "john.doe")
        self.assertEqual(self.admin_user.get_username(), "admin.smith")

    def test_get_name_regular_user(self):
        self.assertEqual(self.regular_user.get_name(), "John Doe")

    def test_get_name_admin_user(self):
        self.assertEqual(self.admin_user.get_name(), "Alice Smith")

    def test_get_name_with_empty_names(self):
        empty_name_user = User("test", "", "", False)

        self.assertEqual(empty_name_user.get_name(), " ")

    def test_to_dict_regular_user(self):
        expected_dict = {
            'username': 'john.doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'admin': False
        }
        self.assertEqual(self.regular_user.to_dict(), expected_dict)

    def test_to_dict_admin_user(self):
        expected_dict = {
            'username': 'admin.smith',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'admin': True
        }
        self.assertEqual(self.admin_user.to_dict(), expected_dict)

    def test_to_dict_default_admin_user(self):
        expected_dict = {
            'username': 'default.user',
            'first_name': 'Dave',
            'last_name': 'Jones',
            'admin': False
        }
        self.assertEqual(self.default_admin_user.to_dict(), expected_dict)

    def test_to_dict_with_empty_strings(self):
        empty_str_user = User(username = "", first_name = "", last_name = "", admin = False)

        expected_dict = {
            'username': '',
            'first_name': '',
            'last_name': '',
            'admin': False
        }
        self.assertEqual(empty_str_user.to_dict(), expected_dict)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)