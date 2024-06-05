from django import forms
from .models import Account, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()

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
