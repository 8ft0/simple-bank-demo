from decouple import config
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from authentication.models import Account  # Adjust import based on your app structure

# Load the OpenAI API key from the environment variables
openai_api_key = config("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("Did not find openai_api_key, please add an environment variable `OPENAI_API_KEY` which contains it, or pass `openai_api_key` as a named parameter.")

# Set up LangChain model with the API key
model = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)

# Define prompt template
prompt = PromptTemplate.from_template("""
Answer the following question based on the provided context:

<context>
{context}
</context>

Question: {input}
""")

def get_account_balance(user_id):
    try:
        account = Account.objects.filter(customers__id=user_id).first()  # Correct query using ManyToManyField
        if account:
            return f"Your account balance is ${account.balance}."
        else:
            return "Account not found."
    except Account.DoesNotExist:
        return "Account not found."

def get_response(user_input, user_id):
    if "balance" in user_input.lower():
        return get_account_balance(user_id)
    
    messages = [HumanMessage(content=user_input)]
    response = model.invoke(messages)
    return response.content

def handle_user_query(user_query, user_id):
    return get_response(user_query, user_id)