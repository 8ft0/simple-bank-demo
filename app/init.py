import os

# Define the directory structure
structure = {
    "authentication": ["__init__.py", "admin.py", "apps.py", "forms.py", "models.py", "tests.py", "urls.py", "utils.py", "views.py"],
    "simple_bank": ["__init__.py", "asgi.py", "settings.py", "urls.py", "wsgi.py"],
    "templates": ["base.html", "register.html", "login.html", "create_account.html", "account_list.html", "deposit.html", "withdraw.html", "transfer.html"],
    ".": ["manage.py", "README.md", "user_guide.md"]
}

# Function to create the directory structure with empty files
def create_structure(structure):
    for directory, files in structure.items():
        if directory != ".":
            os.makedirs(directory, exist_ok=True)
        for file in files:
            with open(os.path.join(directory, file), 'w') as f:
                pass

# Run the function to create the structure
create_structure(structure)

print("Directory structure created successfully!")
