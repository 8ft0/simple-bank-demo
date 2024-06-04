
# SimpleBank

The SimpleBank is a web application built using Django, a popular Python web framework. 

```
├── LICENSE
├── README.md
├── app
│   ├── README.md
│   ├── authentication
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_transaction_balance.py
│   │   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── db.sqlite3
│   ├── files.py
│   ├── init.py
│   ├── manage.py
│   ├── requirements.txt
│   ├── simple_bank
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── templates
│       ├── account_list.html
│       ├── base.html
│       ├── create_account.html
│       ├── deposit.html
│       ├── home.html
│       ├── logged_out.html.html
│       ├── login.html
│       ├── register.html
│       ├── transaction_history.html
│       ├── transfer.html
│       └── withdraw.html
└── docs
    ├── README.md
    ├── User Stories.md
    ├── codebase.md
    ├── features.md
    ├── prompts.md

```

Here is a breakdown of the key components and files included in the project:

### Main Project Structure

- **`simple_bank/`**: This is the main Django project directory containing configuration and setup files.
  - **`asgi.py`**: Configuration for ASGI (Asynchronous Server Gateway Interface).
  - **`settings.py`**: Configuration file for the Django project settings.
  - **`urls.py`**: URL declarations for the project.
  - **`wsgi.py`**: Configuration for WSGI (Web Server Gateway Interface).

### Templates
The templates directory contains HTML files for different parts of the user interface:

- **`base.html`**: Base template that other templates extend.
- **`home.html`**: Homepage template.
- **`login.html`**: Login page template.
- **`register.html`**: Registration page template.
- **`account_list.html`**: List of user accounts.
- **`transaction_history.html`**: User transaction history.
- **`deposit.html`**: Deposit page.
- **`withdraw.html`**: Withdrawal page.
- **`transfer.html`**: Money transfer page.
- **`create_account.html`**: Account creation page.
- **`logged_out.html`**: Logged out page.

### Authentication App
The `authentication` app manages user-related functionalities:


- **`models.py`**: Defines the data models for authentication and user management.
- **`forms.py`**: Contains forms used in authentication processes.
- **`views.py`**: View functions to handle authentication-related requests.
- **`urls.py`**: URL patterns for authentication.
- **`admin.py`**: Configuration for the Django admin interface.
- **`tests.py`**: Test cases for authentication functionalities.
- **`apps.py`**: Configuration for the authentication app.
- **`utils.py`**: Utility functions for authentication.

### Other Files

- **`README.md`**: Provides an overview of the project, setup instructions, and other relevant information.
- **`requirements.txt`**: Lists the dependencies required to run the project.
- **`user_guide.md`**: Likely contains a user guide or documentation for the app.
- **`manage.py`**: A command-line utility to interact with the Django project.

### Overview of the App

The SimpleBank app is designed to manage basic banking operations, including:
- User registration and authentication.
- Viewing account balances and transaction history.
- Performing deposits, withdrawals, and transfers.

The application uses HTML templates for the front-end, Django views and models for the back-end, and standard Django configuration files to manage settings and routing.

