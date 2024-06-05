import unittest
from ..chat import handle_user_query

class TestChatService(unittest.TestCase):

    def test_get_balance_query(self):
        user_id = 1  # Use a valid user_id from your test database
        response = handle_user_query("What is my account balance?", user_id)
        self.assertIn("Your account balance is $", response)

    def test_general_query(self):
        user_id = 1  # Use a valid user_id from your test database
        response = handle_user_query("Tell me a joke", user_id)
        self.assertIsInstance(response, str)

if __name__ == "__main__":
    unittest.main()
