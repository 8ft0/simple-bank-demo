from django.test import TestCase
from accounts.models import Account, Transaction
from django.contrib.auth.models import User
from chat.chat import deposit_money, withdraw_money, transfer_money

class AccountOperationsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.source_account = Account.objects.create(account_number='0001', balance=1000)
        self.target_account = Account.objects.create(account_number='0002', balance=500)
        self.source_account.customers.add(self.user)

    def test_deposit_money(self):
        response = deposit_money(self.user.id, 100)
        self.assertEqual(response, "Deposited $100 to your account.")
        self.source_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, 1100)
        self.assertTrue(Transaction.objects.filter(account=self.source_account, transaction_type='deposit', amount=100).exists())

    def test_withdraw_money_success(self):
        response = withdraw_money(self.user.id, 100)
        self.assertEqual(response, "Withdrew $100 from your account.")
        self.source_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, 900)
        self.assertTrue(Transaction.objects.filter(account=self.source_account, transaction_type='withdrawal', amount=100).exists())

    def test_withdraw_money_insufficient_funds(self):
        response = withdraw_money(self.user.id, 2000)
        self.assertEqual(response, "Insufficient funds.")
        self.source_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, 1000)
        self.assertFalse(Transaction.objects.filter(account=self.source_account, transaction_type='withdrawal', amount=2000).exists())

    def test_transfer_money_success(self):
        response = transfer_money(self.user.id, '0002', 100)
        self.assertEqual(response, "Transferred $100 to account 0002.")
        self.source_account.refresh_from_db()
        self.target_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, 900)
        self.assertEqual(self.target_account.balance, 600)
        self.assertTrue(Transaction.objects.filter(account=self.source_account, transaction_type='transfer', amount=100).exists())
        self.assertTrue(Transaction.objects.filter(account=self.target_account, transaction_type='transfer', amount=100).exists())

    def test_transfer_money_insufficient_funds(self):
        response = transfer_money(self.user.id, '0002', 2000)
        self.assertEqual(response, "Insufficient funds.")
        self.source_account.refresh_from_db()
        self.target_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, 1000)
        self.assertEqual(self.target_account.balance, 500)
        self.assertFalse(Transaction.objects.filter(account=self.source_account, transaction_type='transfer', amount=2000).exists())
        self.assertFalse(Transaction.objects.filter(account=self.target_account, transaction_type='transfer', amount=2000).exists())
