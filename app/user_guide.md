# Simple Bank User Guide

## Getting Started
- Register a new user account.
- Log in with your credentials.

## Managing Accounts
- **Create an Account:**
  - Navigate to "Create Account" from the menu.
  - Enter the account number and submit the form.

- **View Accounts:**
  - Navigate to "My Accounts" to see a list of your accounts and their balances.

- **Delete an Account:**
  - In the "My Accounts" list, click "Delete" next to the account you wish to remove.

## Performing Transactions
- **Deposit:**
  - Navigate to "My Accounts" and select the account to deposit into.
  - Click "Deposit," enter the amount, and submit the form.

- **Withdraw:**
  - Navigate to "My Accounts" and select the account to withdraw from.
  - Click "Withdraw," enter the amount, and submit the form.

- **Transfer:**
  - Navigate to "My Accounts" and select the account to transfer from.
  - Click "Transfer," enter the target account number, amount, and description, then submit the form.

## Notifications
- You will receive email notifications for deposits, withdrawals, and transfers.
- Low balance alerts will be sent if your account balance drops below a specified threshold.

## Support
- For support, contact us at support@example.com.


---

To run the Simple Bank application, follow these steps:

1. **Clone the Repository:**
   If you haven't already, clone the project repository to your local machine:
   ```bash
   git clone https://github.com/your-repo/simple-bank.git
   cd simple-bank
   ```

2. **Set Up a Virtual Environment:**
   It's recommended to use a virtual environment to manage your project dependencies. You can set up a virtual environment using `venv` or `virtualenv`:
   ```bash
   python -m venv env
   source env/bin/activate   # On Windows use `env\Scripts\activate`
   ```

3. **Install Dependencies:**
   Install the required dependencies listed in the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database:**
   Apply the migrations to set up the database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a Superuser:**
   Create a superuser account to access the Django admin interface:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Development Server:**
   Start the Django development server:
   ```bash
   python manage.py runserver
   ```

7. **Access the Application:**
   Open your web browser and navigate to `http://127.0.0.1:8000/` to access the application.

8. **Register and Login:**
   - Register a new user account.
   - Log in with your credentials.

9. **Manage Accounts and Perform Transactions:**
   - Create, view, and manage accounts.
   - Perform transactions (deposit, withdraw, transfer).
   - Receive email notifications for significant transactions and low balances.

### Additional Information

- **Admin Interface:**
  You can access the Django admin interface at `http://127.0.0.1:8000/admin/` using the superuser credentials.

- **Testing:**
  To run the tests and ensure everything is working correctly, use:
  ```bash
  python manage.py test
  ```

Feel free to refer to the `README.md` and `user_guide.md` files for more detailed instructions and information about the application.