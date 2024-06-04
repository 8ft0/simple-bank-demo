import os

# Define the file content
file_contents = {
    "simple_bank/authentication/models.py": """
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Account(models.Model):
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    customers = models.ManyToManyField(User, related_name='accounts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account_number

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
    """,
    "simple_bank/authentication/forms.py": """
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class AccountCreationForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_number']

class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']

class TransferForm(forms.ModelForm):
    target_account = forms.CharField(max_length=20)

    class Meta:
        model = Transaction
        fields = ['amount', 'description']
    """,
    "simple_bank/authentication/views.py": """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Account, Transaction
from .forms import DepositForm, WithdrawalForm, TransferForm, AccountCreationForm, CustomerRegistrationForm
from .utils import send_notification

@login_required
def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomerRegistrationForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@login_required
def create_account(request):
    if request.method == "POST":
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.save()
            account.customers.add(request.user)
            return redirect('account_list')
    else:
        form = AccountCreationForm()
    return render(request, 'create_account.html', {'form': form})

@login_required
def delete_account(request, account_id):
    account = Account.objects.get(id=account_id)
    if request.user in account.customers.all():
        account.delete()
    return redirect('account_list')

@login_required
def account_list(request):
    accounts = request.user.accounts.all()
    return render(request, 'account_list.html', {'accounts': accounts})

@login_required
def deposit(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = account
            transaction.transaction_type = 'deposit'
            transaction.save()
            account.balance += transaction.amount
            account.save()
            messages.success(request, 'Deposit successful')
            send_notification(
                request.user.email,
                'Deposit Notification',
                f'You have successfully deposited {transaction.amount} to account {account.account_number}.'
            )
            return redirect('account_list')
        else:
            messages.error(request, 'Invalid input')
    else:
        form = DepositForm()
    return render(request, 'deposit.html', {'form': form, 'account': account})

@login_required
def withdraw(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    if request.method == "POST":
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = account
            transaction.transaction_type = 'withdrawal'
            if account.balance >= transaction.amount:
                transaction.save()
                account.balance -= transaction.amount
                account.save()
                messages.success(request, 'Withdrawal successful')
                send_notification(
                    request.user.email,
                    'Withdrawal Notification',
                    f'You have successfully withdrawn {transaction.amount} from account {account.account_number}.'
                )
                if account.balance < 50.00:
                    send_notification(
                        request.user.email,
                        'Low Balance Alert',
                        f'Your account {account.account_number} has a low balance of {account.balance}.'
                    )
                return redirect('account_list')
            else:
                form.add_error('amount', 'Insufficient funds')
                messages.error(request, 'Insufficient funds')
        else:
            messages.error(request, 'Invalid input')
    else:
        form = WithdrawalForm()
    return render(request, 'withdraw.html', {'form': form, 'account': account})

@login_required
def transfer(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    if request.method == "POST":
        form = TransferForm(request.POST)
        if form.is_valid():
            target_account_number = form.cleaned_data['target_account']
            target_account = get_object_or_404(Account, account_number=target_account_number)
            transaction = form.save(commit=False)
            transaction.account = account
            transaction.transaction_type = 'transfer'
            if account.balance >= transaction.amount:
                transaction.save()
                account.balance -= transaction.amount
                target_account.balance += transaction.amount
                account.save()
                target_account.save()
                messages.success(request, 'Transfer successful')
                send_notification(
                    request.user.email,
                    'Transfer Notification',
                    f'You have successfully transferred {transaction.amount} from account {account.account_number} to account {target_account.account_number}.'
                )
                send_notification(
                    target_account.customers.first().email,
                    'Transfer Received',
                    f'You have received a transfer of {transaction.amount} to your account {target_account.account_number}.'
                )
                return redirect('account_list')
            else:
                form.add_error('amount', 'Insufficient funds')
                messages.error(request, 'Insufficient funds')
        else:
            messages.error(request, 'Invalid input')
    else:
        form = TransferForm()
    return render(request, 'transfer.html', {'form': form, 'account': account})
    """,
    "simple_bank/authentication/tests.py": """
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
        self.assertEqual(response.status_code, 302)  # Redirect after successful account creation
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
    """,
    "simple_bank/authentication/urls.py": """
from django.urls import path
from .views import register, login_view, home, create_account, delete_account, account_list, deposit, withdraw, transfer

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('home/', home, name='home'),
    path('create_account/', create_account, name='create_account'),
    path('delete_account/<int:account_id>/', delete_account, name='delete_account'),
    path('accounts/', account_list, name='account_list'),
    path('deposit/<int:account_id>/', deposit, name='deposit'),
    path('withdraw/<int:account_id>/', withdraw, name='withdraw'),
    path('transfer/<int:account_id>/', transfer, name='transfer'),
]
    """,
    "simple_bank/simple_bank/settings.py": """
"""
}

# Write the content to the respective files
for file_path, content in file_contents.items():
    with open(f"./{file_path}", "w") as f:
        f.write(content)

