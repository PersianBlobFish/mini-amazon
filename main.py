import json
import os
import datetime
import random
import hashlib
import sqlite3
from user import User
from catalog import Catalog
from product import Product

# Define file name
FILE_NAME = "users.json"

# Initialize SQLite database connection
con = sqlite3.connect("user.db")
cur = con.cursor()

# Create users table if it doesn't exist
def init_db():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            name TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    con.commit() # Forgot to add Admin user

init_db()

# Load existing users or initialize empty data
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as file:
        data = json.load(file)
else:
    data = {"users": [], "catalog": []}

# Convert user dicts to User objects
data["users"] = [User.from_dict(u) for u in data["users"]]
catalog = Catalog.from_list(data["catalog"]) if "catalog" in data else Catalog()

# Save all data back to JSON file
def save_all_data():
    # convert users back to dicts before saving
    serializable = {
        **data,
        "users": [u.to_dict() for u in data["users"]],
        "catalog": catalog.to_list()
    }
    # Save to JSON file
    with open(FILE_NAME, "w") as file:
        json.dump(serializable, file, indent=4)

# Authentication function
def login(username, password_hash):
    query = "SELECT * FROM users WHERE name = ? AND password = ?" # Use parameterized query to prevent SQL injection (? placeholders)
    cur.execute(query, (username, password_hash))
    result = cur.fetchone()
    # If a matching user is found, return True. Otherwise, return False.
    if result:
        for user in data["users"]:
            if user.username == username:
                return True
    return False

# Prompt user for password and return its hash (checking for minimum length)
def prompt_password(min_len=6):
    while True:
        pw = input(f"Choose a password (min {min_len} chars): ")
        if len(pw) >= min_len:
            return hashlib.sha256(pw.encode()).hexdigest() # Return the hash of the password
        print("Password too short! Try again.")

# Registration function
def register(username, password_hash=None, min_len=6):
    # Ask for password if not provided
    if password_hash is None:
        password_hash = prompt_password(min_len)


    # Check duplicate username
    for user in data["users"]:
        if user.username == username:
            return False  # Username already exists

    # Save user
    data["users"].append(User(username, cart=[]))
    cur.execute("INSERT INTO users (name, password) VALUES (?, ?)", (username, password_hash))
    con.commit()
    save_all_data()
    return True

# Helper function to get User object by username
def get_user(username: str):
    for u in data["users"]:
        if u.username == username:
            return u
    return None

# Cart management functions
def add_to_cart(catalog: Catalog, cart):
    print("Available products:")
    for p in catalog.list_all():
        print(f"ID: {p.id}, Title: {p.title}, Price: ${p.price}, Stock: {p.stock}") # Display stock information when listing products

    # Get user input for product ID and quantity, with error handling
    try:
        product_id = int(input("Enter the product ID to add to cart: "))
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return

    # Check if product ID exists and if enough stock is available
    product = catalog.get_by_id(product_id)
    if not product:
        print("Product ID not found.")
        return
    
    # Check stock availability before adding to cart
    if not catalog.has_stock(product_id, quantity):
        print(f"Only {product.stock} items available in stock.")
        return
    # Form the cart item and add to cart
    cart.append({
        "id": product.id,
        "title": product.title,
        "price": product.price,
        "quantity": quantity
    })
    print("Product ID not found.")

# Remove item from cart by index, with error handling
def remove_from_cart(cart):
    if not cart:
        print("Your cart is empty.")
        return

    # Display cart items with indices for user to choose from
    print("Items in your cart:")
    for idx, item in enumerate(cart):
        print(f"{idx + 1}. {item['title']} - ${item['price']} x {item['quantity']}")

    # Get user input for item index to remove, with error handling
    try:
        item_idx = int(input("Enter the item number to remove from cart: ")) - 1 # Convert to 0-based index
        if 0 <= item_idx < len(cart):
            removed_item = cart.pop(item_idx)
            print(f"Removed {removed_item['title']} from cart.")
        else:
            print("Invalid item number.")
    except ValueError:
        print("Invalid input. Please enter a numeric value.")

# Display cart contents and total price
def view_cart(cart):
    if not cart:
        print("Your cart is empty.")
        return

    print("Your cart contains:") # Display cart items with details
    total = 0
    for item in cart:
        item_total = item['price'] * item['quantity']
        total += item_total
        print(f"{item['title']} - ${item['price']} x {item['quantity']} = ${item_total:.2f}")
    print(f"Total: ${total:.2f}")

# Save cart by saving all data (users and catalog) to the JSON file
def save_cart(user: User):
    save_all_data()  # Save all data including users and their carts
    print("Cart saved successfully.")

# Checkout function that verifies stock, generates receipt, reduces stock, and clears cart
def checkout(user):
    cart = user.cart
    if not cart:
        print("Your cart is empty.")
        return
    
    # Verify stock before charging/receipt
    for item in cart:
        if not catalog.has_stock(item["id"], item["quantity"]):
            p = catalog.get_by_id(item["id"])
            available = p.stock if p else 0
            print(f"Not enough stock for item id {item['id']}. Available: {available}. Checkout cancelled.")
            return

    # Display cart contents and total before confirming purchase
    print("Checking out the following items:")
    total = 0

    # Display each item with its total price and calculate the overall total
    for item in cart:
        item_total = item['price'] * item['quantity']
        total += item_total
        print(f"{item['title']} - ${item['price']} x {item['quantity']} = ${item_total:.2f}")
    print(f"Total amount due: ${total:.2f}")

    # Receipt generation and stock reduction
    with open("receipt.txt", "a") as f:
        f.write("--- New Purchase ---\n")
        x = datetime.datetime.now()
        f.write("Order ID: " + str(random.randint(1000,9999)) + "\n")
        f.write("User: " + user.username + "\n")
        f.write(x.strftime("%c") + "\n")
        for item in cart:
            f.write(
                    f"{item['title']} - ${item['price']} x {item['quantity']} = "
                    f"${item['price'] * item['quantity']:.2f}\n"
            )

    # Reduce stock for each item in the cart
    for item in cart:
        catalog.reduce_stock(item["id"], item["quantity"])

    # Clear cart and save data
    cart.clear()
    save_all_data()  # Save updated stock and cleared cart
    print("Thank you for your purchase!")

# Main menu function that displays options and handles user input, with admin panel access for admin users
def menu(user: User):
    cart = user.cart  # use the cart from the User object
    while True:
        print(f"Welcome to the Shop System")
        print("1.Add to cart")
        print("2.Remove from cart")
        print("3.View cart")
        print("4.Save cart")
        print("5.Checkout")
        print("6.Exit")
        if user.username == "admin":
            print("7.Admin panel")
        print("---------------------")
        match input("Choose an option (1-6): ").strip():
            case "1":
                add_to_cart(catalog, cart)
                print("---------------------")
            case "2":
                remove_from_cart(cart)
                print("Item removed from cart.")
                print("---------------------")
            case "3":
                print("Viewing cart...")
                view_cart(cart)
                print("---------------------")
            case "4":
                print("Saving cart...")
                save_cart(user)
                print("Cart saved.")
                print("---------------------")
            case "5":
                print("Checking out...")
                checkout(user)
                print("---------------------")
            case "6":
                print("Exiting menu.")
                print("---------------------")
                return
            case "7" if user.username == "admin":
                print("Accessing admin panel...")
                admin_panel()
                print("---------------------")
            case _:
                print("Invalid choice")
                print("---------------------")

# Admin panel function that allows admin users to view users/products, add/remove products, and access SQLite command prompt
def admin_panel():
    while True:
        print("Admin Panel")
        print("1. View all users")
        print("2. View all products")
        print("3. Add new product")
        print("4. Remove product")
        print("5. Sqlite command prompt")
        print("6. Exit")
        choice = input("Choose an option (1-6): ").strip()

        match choice:
            case "1":
                print("All registered users:")
                for user in data["users"]:
                    print(f"- {user.username}")
            case "2":
                print("Product catalog:")
                for product in catalog.list_all():
                    print(f"ID: {product.id}, Title: {product.title}, Price: ${product.price}, Stock: {product.stock}")
            case "3":
                title = input("Product title: ")

                try:
                    price = float(input("Product price: "))
                    stock = int(input("Product stock: "))
                except ValueError:
                    print("Invalid input for price or stock. Please enter numeric values.")
                    continue

                category = input("Product category: ")

                # Auto-generate a new ID
                new_id = max([p.id for p in catalog.products], default=0) + 1

                product = Product( # Format the new product with the generated ID and user input
                    id=new_id,
                    title=title,
                    price=price,
                    stock=stock,
                    category=category
                )

                # Add the new product to the catalog and save data, with error handling for duplicate IDs
                try:
                    catalog.add_product(product)
                    save_all_data()  # Save the new product to the file
                    print("Product added successfully!")
                except ValueError as e:
                    print(e)
            case "4":
                try:
                    product_id = int(input("Enter the product ID to remove: "))
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")
                    continue
                
                # Find the product by ID and remove it from the catalog, with error handling for non-existent IDs
                product = catalog.get_by_id(product_id)
                if product:
                    catalog.products.remove(product)
                    save_all_data()  # Save the updated catalog to the file
                    print("Product removed successfully!")
                else:
                    print("Product ID not found.")
            case "5":
                print("Entering SQLite command prompt. Type 'exit' to return.") # Simple command prompt for executing raw SQL commands against the user.db database, with error handling
                while True:                                                     # Note: This is one risky one, as it allows executing arbitrary SQL commands.
                    cmd = input("SQL> ").strip()
                    if cmd.lower() == "exit":
                        print("Exiting SQLite prompt.")
                        break
                    try:
                        cur.execute(cmd) # Execute the command and print results if it's a SELECT query, otherwise commit changes
                        if cmd.lower().startswith("select"):
                            rows = cur.fetchall()
                            for row in rows:
                                print(row)
                        else:
                            con.commit()
                            print("Command executed successfully.")
                    except Exception as e:
                        print(f"Error executing command: {e}")
            case "6": # Exit the admin panel and return to the main menu
                print("Exiting admin panel.")
                return
            case _:
                print("Invalid choice. Please select a valid option.")


# Main function that displays the initial login/register menu and handles user authentication, with a loop to allow multiple attempts and access to the main menu upon successful login
def main():
    while True:
        choice = input("Type 'login', 'register', or 'exit': ").strip().lower()

        match choice:
            case "login":
                global username # Note: I'm pretty sure, i had a sollution to this, but i forgot it
                username = input("Username: ")
                password = input("Password: ")
                password_hash = hashlib.sha256(password.encode()).hexdigest()

                # Authenticate user
                if login(username, password_hash):
                    print(f"Login successful, Welcome! {username}")
                    user = get_user(username)
                    if user is not None:
                        menu(user) # pass the User object to the menu
                else:
                    print("Invalid username or password")

            # Registration flow that prompts for username and password
            case "register":
                username = input("Choose a username: ")
                if username == "Admin":
                    print("Username unavaliable")
                else:
                    password = prompt_password(6)
                    print("Registration successful" if register(username, password) else "Username already exists")

            case "exit":
                print("Good bye!")
                break

            case _:
                print("Invalid choice")

main()