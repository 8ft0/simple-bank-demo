from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
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
            transaction.balance = account.balance + transaction.amount  # Calculate balance after deposit
            transaction.save()
            account.balance = transaction.balance
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
                transaction.balance = account.balance - transaction.amount  # Calculate balance after withdrawal
                transaction.save()
                account.balance = transaction.balance
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
            transaction.description = f'Transfer to account {target_account.account_number}'
            if account.balance >= transaction.amount:
                # Create transaction for the source account
                transaction.balance = account.balance - transaction.amount
                transaction.save()
                account.balance = transaction.balance
                account.save()
                
                # Create transaction for the target account
                target_transaction = Transaction(
                    account=target_account,
                    transaction_type='transfer',
                    amount=transaction.amount,
                    balance=target_account.balance + transaction.amount,
                    description=f'Transfer from account {account.account_number}'
                )
                target_transaction.save()
                target_account.balance = target_transaction.balance
                target_account.save()
                
                messages.success(request, 'Transfer successful')
                send_notification(
                    request.user.email,
                    'Transfer Notification',
                    f'You have successfully transferred {transaction.amount} from account {account.account_number} to account {target_account.account_number}.'
                )
                target_customer = target_account.customers.first()
                if target_customer:
                    send_notification(
                        target_customer.email,
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




@login_required
def transaction_history(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    transactions = account.transactions.all()
    
    total_debits = sum(transaction.amount for transaction in transactions if transaction.transaction_type in ['withdrawal', 'transfer'] and transaction.amount > 0)
    total_credits = sum(transaction.amount for transaction in transactions if transaction.transaction_type == 'deposit' or (transaction.transaction_type == 'transfer' and transaction.amount < 0))
    
    return render(request, 'transaction_history.html', {
        'account': account,
        'transactions': transactions,
        'total_debits': total_debits,
        'total_credits': total_credits
    })
