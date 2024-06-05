from django.test import TestCase
from accounts.models import Account
from django.contrib.auth.models import User
from chat.chat import transfer_money

class TransferMoneyTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.source_account = Account.objects.create(account_number='0001', balance=1000)
        self.target_account = Account.objects.create(account_number='0002', balance=500)
        self.source_account.customers.add(self.user)

    def test_transfer_money_success(self):
        response = transfer_money(self.user.id, '0002', 100)
        self.assertEqual(response, "Transferred $100 to account 0002.")
        self.source_account.refresh_from_db()
        self.target_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, 900)
        self.assertEqual(self.target_account.balance, 600)

    def test_transfer_money_insufficient_funds(self):
        response = transfer_money(self.user.id, '0002', 2000)
        self.assertEqual(response, "Insufficient funds.")
        self.source_account.refresh_from_db()
        self.target_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, 1000)
        self.assertEqual(self.target_account.balance, 500)

    def test_transfer_money_account_not_found(self):
        response = transfer_money(self.user.id, '9999', 100)
        self.assertEqual(response, "Source or target account not found.")