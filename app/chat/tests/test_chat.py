from django.test import TestCase
from django.contrib.auth import get_user_model

from chat.chat import handle_user_query
from accounts.models import Account

User = get_user_model()

class TestChatService(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='Testpassword123')
        self.account = Account.objects.create(account_number='1234567890', balance=100.00)
        self.account.customers.add(self.user)
        self.client.login(username='testuser', password='Testpassword123')

    def test_get_balance_query(self):
        response = handle_user_query("What is my account balance?", self.user.id)
        self.assertIn("Your account balance is $100", response)

    def test_general_query(self):
        response = handle_user_query("Tell me a joke", self.user.id)
        self.assertIsInstance(response, str)

if __name__ == "__main__":
    unittest.main()