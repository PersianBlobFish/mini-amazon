import json
import os
import datetime
import random
import hashlib
from user import User
from catalog import Catalog

FILE_NAME = "users.json"


# Load existing users or initialize empty data
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as file:
        data = json.load(file)
else:
    data = {"users": [], "catalog": []}

data["users"] = [User.from_dict(u) for u in data["users"]]
catalog = Catalog.from_list(data["catalog"]) if "catalog" in data else Catalog()

def save_all_data():
    # convert users back to dicts before saving
    serializable = {
        **data,
        "users": [u.to_dict() for u in data["users"]],
        "catalog": catalog.to_list()
    }
    with open(FILE_NAME, "w") as file:
        json.dump(serializable, file, indent=4)

def login(username, password_hash):
    for user in data["users"]:
        if user.username == username and user.password_hash == password_hash:
            return True
    return False

def prompt_password(min_len=6):
    while True:
        pw = input(f"Choose a password (min {min_len} chars): ")
        if len(pw) >= min_len:
            return hashlib.sha256(pw.encode()).hexdigest()
        print("Password too short! Try again.")

def register(username, password_hash=None, min_len=6):
    # ask for password if not provided
    if password_hash is None:
        password_hash = prompt_password(min_len)


    # check duplicate username
    for user in data["users"]:
        if user.username == username:
            return False  # Username already exists

    # save user
    data["users"].append(User(username, password_hash, cart=[]))
    save_all_data()
    return True

def get_user(username: str):
    for u in data["users"]:
        if u.username == username:
            return u
    return None

def add_to_cart(catalog: Catalog, cart):
    print("Available products:")
    for p in catalog.list_all():
        print(f"ID: {p.id}, Title: {p.title}, Price: ${p.price}, Stock: {p.stock}")

    try:
        product_id = int(input("Enter the product ID to add to cart: "))
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return

    product = catalog.get_by_id(product_id)
    if not product:
        print("Product ID not found.")
        return
    
    if not catalog.has_stock(product_id, quantity):
        print(f"Only {product.stock} items available in stock.")
        return
    cart.append({
        "id": product.id,
        "title": product.title,
        "price": product.price,
        "quantity": quantity
    })
    print("Product ID not found.")

def remove_from_cart(cart):
    if not cart:
        print("Your cart is empty.")
        return

    print("Items in your cart:")
    for idx, item in enumerate(cart):
        print(f"{idx + 1}. {item['title']} - ${item['price']} x {item['quantity']}")

    try:
        item_idx = int(input("Enter the item number to remove from cart: ")) - 1
        if 0 <= item_idx < len(cart):
            removed_item = cart.pop(item_idx)
            print(f"Removed {removed_item['title']} from cart.")
        else:
            print("Invalid item number.")
    except ValueError:
        print("Invalid input. Please enter a numeric value.")

def view_cart(cart):
    if not cart:
        print("Your cart is empty.")
        return

    print("Your cart contains:")
    total = 0
    for item in cart:
        item_total = item['price'] * item['quantity']
        total += item_total
        print(f"{item['title']} - ${item['price']} x {item['quantity']} = ${item_total:.2f}")
    print(f"Total: ${total:.2f}")

def save_cart(user: User):
    save_all_data()  # Save all data including users and their carts
    print("Cart saved successfully.")

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

    print("Checking out the following items:")
    total = 0

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
            case _:
                print("Invalid choice")
                print("---------------------")



def main():
    while True:
        choice = input("Type 'login', 'register', or 'exit': ").strip().lower()

        match choice:
            case "login":
                global username
                username = input("Username: ")
                password = input("Password: ")
                password_hash = hashlib.sha256(password.encode()).hexdigest()

                if login(username, password_hash):
                    print(f"Login successful, Welcome! {username}")
                    user = get_user(username)
                    if user is not None:
                        menu(user) # pass the User object to the menu
                else:
                    print("Invalid username or password")

            case "register":
                username = input("Choose a username: ")
                if username == "Admin":
                    print("Username unavaliable")
                else:
                    password = prompt_password(6)
                    print("Registration successful" if register(username, password) else "Username already exists")

            case "exit":
                print("Bye!")
                break

            case _:
                print("Invalid choice")

main()