from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Account

User = get_user_model()

class AuthenticationTests(TestCase):

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        user = User.objects.create_user(username='testuser', email='testuser@example.com', password='Testpassword123')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'Testpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

class AccountManagementTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='Testpassword123')
        self.client.login(username='testuser', password='Testpassword123')

    def test_create_account(self):
        response = self.client.post(reverse('create_account'), {
            'account_number': '1234567890'
        })
        self.assertEqual(response.status_code,  302)  # Redirect after successful account creation
        self.assertTrue(Account.objects.filter(account_number='1234567890').exists())

    def test_delete_account(self):
        account = Account.objects.create(account_number='1234567890')
        account.customers.add(self.user)
        response = self.client.post(reverse('delete_account', args=[account.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful account deletion
        self.assertFalse(Account.objects.filter(account_number='1234567890').exists())

class TransactionManagementTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='Testpassword123')
        self.account = Account.objects.create(account_number='1234567890', balance=100.00)
        self.account.customers.add(self.user)
        self.client.login(username='testuser', password='Testpassword123')

    def test_deposit(self):
        response = self.client.post(reverse('deposit', args=[self.account.id]), {
            'amount': '50.00'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful deposit
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 150.00)

    def test_withdraw(self):
        response = self.client.post(reverse('withdraw', args=[self.account.id]), {
            'amount': '50.00'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful withdrawal
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 50.00)

    def test_transfer(self):
        target_account = Account.objects.create(account_number='0987654321', balance=100.00)
        response = self.client.post(reverse('transfer', args=[self.account.id]), {
            'amount': '50.00',
            'target_account': '0987654321',
            'description': 'Test transfer'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful transfer
        self.account.refresh_from_db()
        target_account.refresh_from_db()
        self.assertEqual(self.account.balance, 50.00)
        self.assertEqual(target_account.balance, 150.00)
