import os
import sys
import re

from decimal import Decimal
from decouple import config
from django.contrib.auth import get_user_model


from accounts.models import Account, Transaction


# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_bank.settings')
import django
django.setup()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from accounts.models import Account

# Load the OpenAI API key from the environment variables
openai_api_key = config("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("Did not find openai_api_key, please add an environment variable `OPENAI_API_KEY` which contains it, or pass `openai_api_key` as a named parameter.")

# Set up LangChain model with the API key
model = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)

User = get_user_model()


# Define prompt template for intent detection
intent_prompt = PromptTemplate.from_template("""
Classify the user's query into one of the following intents: ["get_balance", "get_transactions", "transfer_money", "deposit_money", "withdraw_money", "create_account", "delete_account", "list_accounts", "other"].

Query: {query}

Intent:
""")





# Extract parameters for transfer money intent
def extract_transfer_params(user_input):
    target_account_match = re.search(r'account (\d+)', user_input)
    amount_match = re.search(r'\$(\d+)', user_input)

    if target_account_match and amount_match:
        target_account = target_account_match.group(1)
        amount = amount_match.group(1)
        return target_account, amount
    return None, None


def create_account(user_id, initial_balance=0):
    try:
        user = User.objects.get(id=user_id)
        account_number = f"{user_id:04d}{Account.objects.count() + 1:04d}"
        account = Account.objects.create(account_number=account_number, balance=Decimal(initial_balance))
        account.customers.add(user)
        return f"Account {account_number} created with initial balance ${initial_balance}."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def delete_account(user_id, account_number):
    try:
        account = Account.objects.filter(account_number=account_number, customers__id=user_id).first()
        if account:
            account.delete()
            return f"Account {account_number} deleted."
        else:
            return "Account not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def list_accounts(user_id):
    try:
        accounts = Account.objects.filter(customers__id=user_id)
        if accounts.exists():
            account_list = "\n".join([f"{account.account_number}: ${account.balance}" for account in accounts])
            return f"Your accounts:\n{account_list}"
        else:
            return "No accounts found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Define functions to handle different intents
def get_account_balance(user_id):
    try:
        account = Account.objects.filter(customers__id=user_id).first()
        if account:
            return f"Your account balance is ${account.balance}."
        else:
            return "Account not found."
    except Account.DoesNotExist:
        return "Account not found."

def deposit_money(user_id, amount):
    try:
        amount = Decimal(amount)
        account = Account.objects.filter(customers__id=user_id).first()

        if account:
            account.deposit(amount)
            # Create a transaction record
            Transaction.objects.create(account=account, transaction_type='deposit', amount=amount, balance=account.balance, description='Deposit')
            return f"Deposited ${amount} to your account."
        else:
            return "Account not found."
    except Account.DoesNotExist:
        return "Account not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def withdraw_money(user_id, amount):
    try:
        amount = Decimal(amount)
        account = Account.objects.filter(customers__id=user_id).first()

        if account:
            if account.withdraw(amount):
                # Create a transaction record
                Transaction.objects.create(account=account, transaction_type='withdrawal', amount=amount, balance=account.balance, description='Withdrawal')
                return f"Withdrew ${amount} from your account."
            else:
                return "Insufficient funds."
        else:
            return "Account not found."
    except Account.DoesNotExist:
        return "Account not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def get_transactions(user_id):
    try:
        account = Account.objects.filter(customers__id=user_id).first()
        if account:
            transactions = account.transactions.all()
            return "\n".join([f"{t.transaction_type}: ${t.amount} on {t.timestamp}" for t in transactions])
        else:
            return "Account not found."
    except Account.DoesNotExist:
        return "Account not found."

def transfer_money(user_id, target_account_number, amount):
    try:
        amount = Decimal(amount)
        source_account = Account.objects.filter(customers__id=user_id).first()
        target_account = Account.objects.filter(account_number=target_account_number).first()

        if source_account and target_account:
            if source_account.debit(amount):
                target_account.credit(amount)
                # Create transaction records
                Transaction.objects.create(account=source_account, transaction_type='transfer', amount=amount, balance=source_account.balance, description=f'Transferred to {target_account_number}')
                Transaction.objects.create(account=target_account, transaction_type='transfer', amount=amount, balance=target_account.balance, description=f'Transferred from {source_account.account_number}')
                return f"Transferred ${amount} to account {target_account_number}."
            else:
                return "Insufficient funds."
        else:
            return "Source or target account not found."
    except Account.DoesNotExist:
        return "Source or target account not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Map intents to functions
intent_function_mapping = {
    "get_balance": get_account_balance,
    "get_transactions": get_transactions,
    "transfer_money": transfer_money,
    "deposit_money": deposit_money,
    "withdraw_money": withdraw_money,
    "create_account": create_account,
    "delete_account": delete_account,
    "list_accounts": list_accounts
}

def determine_intent(user_input):
    messages = [HumanMessage(content=intent_prompt.format(query=user_input))]
    response = model.invoke(messages)
    return response.content.strip().lower()

def handle_user_query(user_query, user_id):
    intent = determine_intent(user_query)
    if intent in intent_function_mapping:
        response_function = intent_function_mapping[intent]
        if intent == "transfer_money":
            target_account, amount = extract_transfer_params(user_query)
            if target_account and amount:
                return response_function(user_id, target_account, amount)
            else:
                return "Could not extract transfer details. Please specify the target account and amount."
        elif intent in ["deposit_money", "withdraw_money"]:
            amount_match = re.search(r'\$(\d+)', user_query)
            if amount_match:
                amount = amount_match.group(1)
                return response_function(user_id, amount)
            else:
                return "Could not extract amount. Please specify the amount."
        elif intent == "create_account":
            initial_balance_match = re.search(r'\$(\d+)', user_query)
            initial_balance = initial_balance_match.group(1) if initial_balance_match else 0
            return response_function(user_id, initial_balance)
        elif intent == "delete_account":
            account_number_match = re.search(r'account (\d+)', user_query)
            if account_number_match:
                account_number = account_number_match.group(1)
                return response_function(user_id, account_number)
            else:
                return "Could not extract account number. Please specify the account number."
        return response_function(user_id)
    else:
        return model.invoke([HumanMessage(content=user_query)]).content

if __name__ == "__main__":
    # Example usage for debugging
    user_id = 1  # Replace with a valid user_id from your database
    user_query = "What is my account balance?"
    print(handle_user_query(user_query, user_id))

    user_query = "Show me my recent transactions."
    print(handle_user_query(user_query, user_id))

    user_query = "Transfer $1 to account 0002."
    print(handle_user_query(user_query, user_id))

    while True:
        user_query = input("You: ")
        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = handle_user_query(user_query, user_id)
        print(f"Bot: {response}")