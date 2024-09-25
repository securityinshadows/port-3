"""
Created on Sep, 2024

@author: Ayoub Wahmane/securityinshadows
Copyright (c) <2024> <Ayoub Wahmane>. All rights reserved
"""
import sqlite3
from datetime import datetime
from typing import List
from typing import Optional
import bcrypt

# Create connection & cursor
conn = sqlite3.connect('expense_tracker.db')
c = conn.cursor()

# Create tables if they don't exist already
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);
''')

c.execute('''
CREATE TABLE IF NOT EXISTS expense_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
);
''')

c.execute('''
CREATE TABLE IF NOT EXISTS income_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
);
''')

c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES expense_categories(id)
);
''')

c.execute('''
CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES income_categories(id)
);
''')

c.execute('''
CREATE TABLE IF NOT EXISTS total (
    user_id INTEGER NOT NULL,
    totalexp INTEGER DEFAULT 0,
    totalinc INTEGER DEFAULT 0,
    totalrev INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
''')

conn.commit()  # Commit the table creation
conn.close()   # Close the connection


# Initialize program lists
expenses_list = []
income_list = []
category_list = []
total_list = []
income_cat_list: List[str] = ["salary", "freelance", "other"]

# Connect to the database
def connect_db():
    return sqlite3.connect('expense_tracker.db')

# Register a new user
def register_user(username: str, password: str):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        print("User registered successfully.")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    except Exception as e:
        print(f"An error occurred during registration: {e}")
    finally:
        conn.close()

# Authenticate a user
def authenticate_user(username: str, password: str) -> Optional[int]:
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
        print("User authenticated successfully.")
        return user[0]  # Return user ID
    else:
        print("Authentication failed.")
        return None
conn.close()
# Load information

def load_incat():
    conn = sqlite3.connect('expense_tracker.db')
    c = conn.cursor()
    
    # List of categories to be inserted
    income_cat_list = ["salary", "freelance", "other"]
    
    for category in income_cat_list:
        try:
            c.execute('INSERT OR IGNORE INTO income_categories (category_name) VALUES (?)', (category,))
        except sqlite3.Error as e:
            print(f"An error occurred while inserting category '{category}': {e}")
    
    conn.commit()  # Commit the transaction
    conn.close()   # Close the connection

def load_expenses():
    try:
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        expenses_list.clear()
        
        # Fetch details
        c.execute('''
            SELECT expenses.id, expenses.amount, expense_categories.category_name, expenses.date 
            FROM expenses 
            JOIN expense_categories ON expenses.category_id = expense_categories.id
        ''')
        
        expenses = c.fetchall()
        
        if not expenses:  # Check if the expenses list is empty
            print("No expenses found.")
        
        for expense in expenses:
            if expense[1] is not None:
                expenses_list.append({
                    "ID": expense[0],     # Use the ID from the expenses table
                    "Amount": expense[1],
                    "Category": expense[2],
                    "Date": expense[3],
                })
    except sqlite3.Error as e:
        print(f"An error occurred while loading expenses: {e}")
    finally:
        conn.close()  # Ensure the connection is closed regardless of errors

def load_income():
    try:
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        income_list.clear()
        
        # Fetch details 2.0.
        c.execute('''
            SELECT income.id, income.amount, income_categories.category_name, income.date 
            FROM income 
            JOIN income_categories ON income.category_id = income_categories.id
        ''')
        
        income = c.fetchall()
        
        if not income:  # Check if the income list is empty
            print("No income records found.")
        
        for inc in income:
            if inc[1] is not None:
                income_list.append({
                    "ID": inc[0],   # Use the ID from the income table (again)
                    "Amount": inc[1],
                    "Category": inc[2],
                    "Date": inc[3],
                })
    except sqlite3.Error as e:
        print(f"An error occurred while loading income records: {e}")
    finally:
        conn.close() 
def load_categories():
    conn = sqlite3.connect('expense_tracker.db')
    c = conn.cursor()
    category_list.clear()

    # Get unique categories from expenses
    c.execute('SELECT DISTINCT category_name FROM expense_categories')
    categories = c.fetchall()
    for category in categories:
        category_list.append(category[0])  # Append each category to the category_list

    # Get unique categories from income
    c.execute('SELECT DISTINCT category_name FROM income_categories')
    categories = c.fetchall()
    for category in categories:
        category_list.append(category[0]) 

    conn.close()

# Ensuring date input is correct
def get_valid_date():
    while True:
        date_str = input("Input the date (YYYY-MM-DD or YYYY/MM/DD): ")
        normalized_date_str = date_str.replace('/', '-') # Normalize input
        try:
    # Parse the normalized date string using hyphens
            task_date = datetime.strptime(normalized_date_str, "%Y-%m-%d")
            return task_date.strftime("%Y-%m-%d") # Return as string
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-MM-DD or YYYY/MM/DD format.")

#Main menu prompt
def welcome():
    print("Welcome to SiSh Tracker.\n1 - Create Records \n2 - Category Manager \n3 - Search Records\n4 - Edit Records\np - Print Tracker Report\nd - Delete Records \ne - Exit Program ")

# United functions
def create_records(): 

    while True:
        print("1 - Input expenses \n2 - Input Incomes")
        choice = input("Enter your choice:")
        if choice == "1":
            add_expense()
        elif choice == "2":
            add_income()
        else:
            print("Invalid input, try again.")
            continue
        break
# United function 2.0
def category_manager():
    print("1 - Create Categories \n2 - Delete Categories (Expense only)")
    choice = input("Enter your choice:")
    if choice == "1":
        create_categories()
    elif choice == "2":
        delete_categories()
    else:
        print("Invalid input, try again.")
        return category_manager


def input_expense():
    while True:
        try:
            amount = int(input("Input the expense amount: "))
            if amount <= 0:
                raise ValueError("Amount must be a positive number.")
            break  # Exit loop if input is valid
        except ValueError as e:
            print(f"Invalid input: {e}. Try again.")
    expense_category = select_categories()
    date = get_valid_date() # Get the date as string
    return {
        "Amount": amount,
        "Category": expense_category,
        "Date": date,
 }

def input_income():
    while True:
        try:
            amount = int(input("Input the income amount: "))
            if amount <= 0:
                raise ValueError("Amount must be a positive number.")
            break  # Exit loop if input is valid
        except ValueError as e:
            print(f"Invalid input: {e}. Try again.")
    input_category = select_income_cat()
    date = get_valid_date() # Get the date as string
    return {
        "Amount": amount,
        "Category": input_category,
        "Date": date,
 }
def create_categories():
    category = input("Create a new category: ").strip().lower()
    conn = sqlite3.connect('expense_tracker.db')  # Reconnect to the database
    c = conn.cursor()
    
    try:
        # Insert the category into expense_categories
        c.execute('INSERT INTO expense_categories (category_name) VALUES (?)', (category,))
        # Insert the category into income_categories
        c.execute('INSERT INTO income_categories (category_name) VALUES (?)', (category,))
        conn.commit()  # Commit the transaction
        print("Category saved.")
    except sqlite3.IntegrityError:
        print("Category already exists. Please use a different name.")
    finally:
        conn.close()  # Ensure the connection is closed

def add_expense():
    expense = input_expense()  # Get the expense data
    expenses_list.append(expense)
    print("Expense saved.")

    # Insert into the database
    conn = sqlite3.connect('expense_tracker.db')
    c = conn.cursor()

    # Fetch category_id from expense_categories based on selected category
    c.execute('SELECT id FROM expense_categories WHERE category_name = ?', (expense["Category"],))
    category_id = c.fetchone()
    
    if category_id:
        c.execute('INSERT INTO expenses (amount, category_id, date, user_id) VALUES (?, ?, ?, ?)', 
                  (expense["Amount"], category_id[0], expense["Date"], 1))  # Assuming user_id is 1
        conn.commit()  # Commit the transaction
    else:
        print(f"Category {expense['Category']} does not exist in the database.")
    
    conn.close()  # Close the connection

def add_income():
    income = input_income()  # Get the income data
    income_list.append(income)
    print("Income saved.")

    conn = sqlite3.connect('expense_tracker.db')
    c = conn.cursor()

    # Fetch category_id from income_categories based on selected category
    c.execute('SELECT id FROM income_categories WHERE category_name = ?', (income["Category"],))
    category_id = c.fetchone()
    
    if category_id:
        c.execute('INSERT INTO income (amount, category_id, date, user_id) VALUES (?, ?, ?, ?)', 
                  (income["Amount"], category_id[0], income["Date"], 1))  # Assuming user_id is 1
        conn.commit()  # Commit the transaction
    else:
        print(f"Category {income['Category']} does not exist in the database.")
    
    conn.close()  # Close the connection

def delete_categories():
    if not category_list:
        print("No categories yet.")
        return
    
    print("Select a category to delete:")
    for index, category in enumerate(category_list, start=1):
        print(f"Category #{index}: {category}")
    
    selected_index = int(input("Enter the category number:"))
    
    if 1 <= selected_index <= len(category_list):
        deleted_category = category_list[selected_index - 1]
        confirmation = input(f"Are you sure you want to delete the category '{deleted_category}'? (y/n): ").lower().strip()
        
        if confirmation != 'y':
            print("Category deletion aborted.")
            return
        
        category_list.remove(deleted_category)
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        
        # Update any entries in the expenses table to 'Uncategorized'
        uncategorized = 'Uncategorized'
        c.execute('UPDATE expenses SET category_id = (SELECT id FROM expense_categories WHERE category_name = ?), date = ? WHERE category_id = (SELECT id FROM expense_categories WHERE category_name = ?)', 
                  (uncategorized, uncategorized, deleted_category))
        
        # Delete category from the categories table
        c.execute('DELETE FROM expense_categories WHERE category_name = ?', (deleted_category,))
        
        conn.commit()  # Commit the transaction
        conn.close()

        print(f"Category '{deleted_category}' deleted, and all records with this category have been updated to '{uncategorized}'.")
    else:
        print("Invalid selection. Please try again.")

def select_categories():
    if not category_list:
        print("No categories yet. Create one first.")
        create_categories()
        return select_categories()  # Recursively call after creating

    for index, category in enumerate(category_list, start=1):
        print(f"Category #{index}: {category}")

    selected_input = input("Enter the category number or 'c' to create: ")

    if selected_input.lower() == 'c':
        create_categories()
        return select_categories()  # After creating a category, return to selection

    try:
        selected_index = int(selected_input)  # converting input to an integer
        if 1 <= selected_index <= len(category_list):
            selected_category = category_list[selected_index - 1]
            print(f"You selected: {selected_category}")
            return selected_category
        else:
            print("Invalid selection. Please try again.")
            return select_categories()
    except ValueError:
        print("Invalid input. Please enter a number or 'c' to create a category.")
        return select_categories()

#end

def select_income_cat():
    # Display available categories to the user
    print("Please select an income category from the following options:")
    for idx, category in enumerate(income_cat_list):
        print(f"{idx + 1}. {category}")
    
    # Loop until a valid category is selected
    while True:
        try:
            # Get user input for category selection
            selected = int(input("Enter the number corresponding to your category: "))
            
            # Check if the selection is within the valid range
            if 1 <= selected <= len(income_cat_list):
                print(f"You have selected: {income_cat_list[selected - 1]}")
                return income_cat_list[selected - 1]  # Return the selected category
            else:
                print("Invalid selection. Please choose a number from the list.")
        except ValueError:
            # Handle non-integer inputs
            print("Please enter a valid number.")
def total_expense():
    total_exp = 0
    for expense in expenses_list:
        amount = expense["Amount"]
        if amount is not None:
            total_exp += expense["Amount"]
    return total_exp

def total_income():
    total_inc = 0 # Fixed typo here
    for income in income_list:
        amount = income["Amount"]
        if amount is not None:
            total_inc += income["Amount"]
    return total_inc

def cvs_expense():
    cvs = input("Do you want to print the report in CVS? (y/n)\nEnter your choice: ")
    if cvs.strip().lower() == "y":
        with open("expense_report.csv", "w") as f:
            for expense in expenses_list:
                f.write(f"{expense['Amount']},{expense['Category']},{expense['Date']}\n")
    elif cvs.strip().lower() == "n":
            print("")
    else:
        print("Invalid input, try again.")
        return cvs_expense()

def cvs_income():
    cvs = input("Do you want to print the report in CVS? (y/n)\nEnter your choice: ")
    if cvs.strip().lower() == "y":
        with open("income_report.csv", "w") as f:
            for income in income_list:
                f.write(f"{income['Amount']},{income['Category']},{income['Date']}\n")
    elif cvs.strip().lower() == "n":
            print("")
    else:
        print("Invalid input, try again.")
        return cvs_income()

def cvs_total():
    cvs = input("Do you want to print the report in CVS? (y/n)\nEnter your choice: ")
    if cvs.strip().lower() == "y":
        with open("total_report.csv", "w") as f:
            f.write(f"Total expenses: {total_expense()}\n")
            f.write(f"Total income: {total_income()}\n")
            f.write(f"Total: {total_income() - total_expense()}\n")
    elif cvs.strip().lower() == "n":
            print("")
    else:
        print("Invalid input, try again.")
        return cvs_total()
def print_report():
    print("Would you like to:\n1 - Print Expense Report\n2 - Print Income Report\n3 - Print Full Report")
    print_choice = input("Enter your choice:")
    if print_choice.strip() == "1":
        if not expenses_list:
            print("No expenses to report on.")
            return
        print("Here is your expense report:")
        for index, expense in enumerate(expenses_list, start=1):
            print(f"Expense #{index}:")
            for key, value in expense.items():
                print(f"  {key}: {value}")
            cvs_expense()
        
    elif print_choice.strip() == "2":
        if not income_list:
            print("No income to report on.")
            return
        print("Here is your income report:")
        for index, income in enumerate(income_list, start=1):
            print(f"Income #{index}:")
            for key, value in income.items():
                print(f"  {key}: {value}")
        cvs_income()
    elif print_choice.strip() == "3":
        if not expenses_list and not income_list:
            print("No transactions to report on.")
            return
        print("Here is your full report:")
        if expenses_list:
            for index, expense in enumerate(expenses_list, start=1):
                print(f"Expense #{index}:")
                for key, value in expense.items():
                    print(f"  {key}: {value}")
    
                print("Total expenses:", total_expense())

        if income_list:
            for index, income in enumerate(income_list, start=1):
                print(f"Income #{index}:")
                for key, value in income.items():
                    print(f"  {key}: {value}")
                print("Total income:", total_income())

        print("Total:",total_income() - total_expense())
        cvs_total()
    else:
        print("Invalid input, try 1, 2, or 3 again.")

def search_records():
    if not expenses_list and not income_list:
        print("No records to search.")
        return
    print("Would you like to:\ne - Search expenses\ni - Search income\nv - View all Records")
    print_choice = input("Enter your choice:")
    if print_choice.strip().lower() == "e":
        search_expense()
    elif print_choice.strip().lower() == "i":
        search_income()
    elif print_choice.strip().lower() == "v":
        view_records()
    else:
        print("Invalid input, try again.")

def view_records():
    if not expenses_list and not income_list:
        print("No records to view.")
        return
    print("Would you like to:\ne - View Expenses\ni - View income")
    print_choice = input("Enter your choice:")
    if print_choice.strip().lower() == "e":
        view_expense()
    elif print_choice.strip().lower() == "i":
        view_income()
    else:
        print("Invalid input, try again.")
        return view_records()
def view_income():
    if not income_list:
        print("No income yet.")
        return
    for index, income in enumerate(income_list, start=1):
        print(f"Income #{index}:")
        for key, value in income.items():
            print(f"  {key}: {value}")

def view_expense():
    if not expenses_list:
        print("No expenses yet.")
        return
    for index, expense in enumerate(expenses_list, start=1):
        print(f"Expense #{index}:")
        for key, value in expense.items():
            print(f"  {key}: {value}")

def edit_inc():
    if not income_list:
        print("No income records yet.")
        return

 # Print income list
    for index, income in enumerate(income_list, start=1):
        print(f"Income #{index}:")
        for key, value in income.items():
            print(f" {key}: {value}")

 # Select record to edit
    try:
        edit_income = int(input("Enter the income record number you want to edit: ")) - 1
        if 0 <= edit_income < len(income_list):
            print("What would you like to edit?\n1 - Amount\n2 - Category\n3 - Date")
            edit_choice = input("Enter your choice:").strip()
            conn = sqlite3.connect('expense_tracker.db')
            c = conn.cursor()

  # Editing Amount
            if edit_choice == "1":
                new_amount = int(input("Enter the new amount: "))
                income_list[edit_income]["Amount"] = new_amount
                c.execute('UPDATE income SET amount = ? WHERE id = ?', 
                (new_amount, income_list[edit_income]['ID']))

  # Editing Category
            elif edit_choice == "2":
                print("Choose a new category:")
                for i, cat in enumerate(income_cat_list, start=1):
                    print(f"{i} - {cat}")
                    new_category_index = int(input("Select category number: ")) - 1
                if 0 <= new_category_index < len(income_cat_list):
                    new_category = income_cat_list[new_category_index]
                    income_list[edit_income]["Category"] = new_category
                    c.execute('UPDATE income SET category_id = (SELECT id FROM income_categories WHERE category_name = ?) WHERE id = ?', 
                    (new_category, income_list[edit_income]['ID']))
                else:
                    print("Invalid category number.")
                    return
  # Editing Date
            elif edit_choice == "3":
                new_date = get_valid_date()
                income_list[edit_income]["Date"] = new_date
                c.execute('UPDATE income SET date = ? WHERE id = ?', 
                    (new_date, income_list[edit_income]['ID']))
            else:
                print("Invalid choice.")
                return

            conn.commit()
            conn.close()
            print("Income updated successfully.")
        else:
            print("Invalid income record number.")
    except ValueError:
            print("Please enter a valid number.")
            print("Total income:", total_income())

def edit_exp():
    if not expenses_list:
        print("No expenses yet.")
        return

 # Print expenses list
    for index, expense in enumerate(expenses_list, start=1):
        print(f"Expense #{index}:")
        for key, value in expense.items():
            print(f" {key}: {value}")

 # Select record to edit
    try:
        edit_expense = int(input("Enter the expense record number you want to edit: ")) - 1
        if 0 <= edit_expense < len(expenses_list):
            print("What would you like to edit?\n1 - Amount\n2 - Category\n3 - Date")
            edit_choice = input("Enter your choice:").strip()
            conn = sqlite3.connect('expense_tracker.db')
            c = conn.cursor()

  # Editing Amount
            if edit_choice == "1":
                new_amount = int(input("Enter the new amount: "))
                expenses_list[edit_expense]["Amount"] = new_amount
                c.execute('UPDATE expenses SET amount = ? WHERE id = ?', 
                    (new_amount, expenses_list[edit_expense]['ID']))

  # Editing Category
            elif edit_choice == "2":
                print("Choose a new category:")
                c.execute('SELECT category_name FROM expense_categories')
                categories = c.fetchall()
            for i, (cat,) in enumerate(categories, start=1):
                print(f"{i} - {cat}")
                new_category_index = int(input("Select category number: ")) - 1
                if 0 <= new_category_index < len(categories):
                    new_category = categories[new_category_index][0]
                    expenses_list[edit_expense]["Category"] = new_category
                    c.execute('UPDATE expenses SET category_id = (SELECT id FROM expense_categories WHERE category_name = ?) WHERE id = ?', 
                        (new_category, expenses_list[edit_expense]['ID']))
                else:
                    print("Invalid category number.")
                    return
            # Editing Date
        elif edit_choice == "3":
                new_date = get_valid_date()
                expenses_list[edit_expense]["Date"] = new_date
                c.execute('UPDATE expenses SET date = ? WHERE id = ?', 
                        (new_date, expenses_list[edit_expense]['ID']))
        else:
            print("Invalid choice.")
            return

        conn.commit()
        conn.close()
        print("Expense updated successfully.")
    except ValueError:
            print("Please enter a valid number.")

            print("Total expenses:", total_expense())

def delete_income():
    if not income_list:
        print("No income records yet.")
        return
    # Print income list
    for index, income in enumerate(income_list, start=1):
        print(f"Income #{index}:")
        for key, value in income.items():
            print(f" {key}: {value}")
            try:
                delete_inc = int(input("Enter the income record number you want to delete: ")) - 1
                if 0 <= delete_inc < len(income_list):
                    deleted_income = income_list.pop(delete_inc)

                    conn = sqlite3.connect('expense_tracker.db')
                    c = conn.cursor()
                    c.execute('DELETE FROM income WHERE id = ?', (deleted_income['ID'],))
                    conn.commit()
                    conn.close()
                    print(f"Income record #{delete_inc + 1} deleted successfully.")
                else:
                    print("Invalid record number.")
            except ValueError:
                print("Please enter a valid number.")
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")

def delete_expense():
    if not expenses_list:
        print("No expenses yet.")
        return

 # Print expenses list
    for index, expense in enumerate(expenses_list, start=1):
        print(f"Expense #{index}:")
        for key, value in expense.items():
            print(f" {key}: {value}")

        try:
            delete_exp = int(input("Enter the expense record number you want to delete: ")) - 1
            if 0 <= delete_exp < len(expenses_list):
                deleted_expense = expenses_list.pop(delete_exp)
                conn = sqlite3.connect('expense_tracker.db')
                c = conn.cursor()
                c.execute('DELETE FROM expenses WHERE id = ?', (deleted_expense['ID'],))
                conn.commit()
                conn.close()
                print(f"Expense record #{delete_exp + 1} deleted successfully.")
            else:
                print("Invalid record number.")
        except ValueError:
            print("Please enter a valid number.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
def search_expense():    
    if not expenses_list:
        print("No expenses yet.")
        return
    
    print("Search by:")
    print("1 - Amount")
    print("2 - Category")
    print("3 - Date")
    
    search_choice = input("Enter your choice: ")
    
    if search_choice == "1":
        search_amount = int(input("Enter the amount to search for: "))
        results = [expense for expense in expenses_list if expense['Amount'] == search_amount]
    elif search_choice == "2":
        search_category = input("Enter the category to search for: ").lower()
        results = [expense for expense in expenses_list if expense['Category'].lower() == search_category]
    elif search_choice == "3":
        search_date = input("Enter the date to search for (YYYY-MM-DD): ")
        results = [expense for expense in expenses_list if expense['Date'] == search_date]
    else:
        print("Invalid choice.")
        return
    
    if results:
        for index, expense in enumerate(results, start=1):
            print(f"Expense #{index}:")
            for key, value in expense.items():
                print(f"  {key}: {value}")
            print()  # Separate results with a newline
    else:
        print("No matching records found.")
def search_income():
    if not income_list:
        print("No income yet.")
        return
    
    print("Search by:")
    print("1 - Amount")
    print("2 - Category")
    print("3 - Date")
    
    search_choice = input("Enter your choice: ")
    
    if search_choice == "1":
        search_amount = int(input("Enter the amount to search for: "))
        results = [income for income in income_list if income['Amount'] == search_amount]
    elif search_choice == "2":
        search_category = input("Enter the category to search for: ").lower()
        results = [income for income in income_list if income['Category'].lower() == search_category]
    elif search_choice == "3":
        search_date = input("Enter the date to search for (YYYY-MM-DD): ")
        results = [income for income in income_list if income['Date'] == search_date]
    else:
        print("Invalid choice.")
        return
    
    if results:
        for index, income in enumerate(results, start=1):
            print(f"Income #{index}:")
            for key, value in income.items():
                print(f"  {key}: {value}")
            print()  # Separate results with a newline
    else:
        print("No matching records found.")


def delete_records():
    if not income_list and not expenses_list:
        print("No records to delete.")
        return

    delete_rec = input("e - Delete expense records \ni - Delete income records\n").strip().lower()
    if delete_rec == "e":
        delete_expense()
    elif delete_rec == "i":
        delete_income()
    else:
        print("Invalid input, try again.")
        return delete_records()

def edit_records():
    if not income_list and not expenses_list:
        print("No records to edit.")
        return

    edit_rec = input("e - Edit expense records \ni - Edit income records\n").strip().lower()
    if edit_rec == "e":
        edit_exp()
    elif edit_rec == "i":
        edit_inc()
    else:
        print("Invalid input, try again.")
        return edit_records()

def choices():
    choice = input("Enter your choice:")
    if choice == "1":
        create_records()
    elif choice == "2":
        category_manager()
    elif choice == "3":
        search_records()
    elif choice == "4":
        edit_records()
    elif choice.lower().strip() =="p":
        print_report()
    elif choice.lower().strip() == "d":
        delete_records()
    elif choice.lower().strip() == "e":
        print("Exiting the program...")
        print("See ya.")
        exit()
    else:
        print("Invalid input, try again.")

# Start the application
load_incat()
load_categories()
load_expenses()
load_income()
while True: 
    welcome()
    choices()
    while True:
        mainmenu = input("Return to main menu? (y/n) \n")
        if mainmenu.lower().strip() == "n":
            print("Exiting the program...")
            print("See ya.")
            exit()
        elif mainmenu.lower().strip() == "y":
            break
        else:
            print("Invalid input, try again.")

        




