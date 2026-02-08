import json
import os
import datetime
import random
import hashlib

FILE_NAME = "users.json"


# Load existing users or initialize empty data
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as file:
        data = json.load(file)
else:
    data = {"users": []}

def login(username, password):
    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            return True
    return False

def prompt_password(min_len=6):
    while True:
        pw = input(f"Choose a password (min {min_len} chars): ")
        if len(pw) >= min_len:
            return hashlib.sha256(pw.encode()).hexdigest()
        print("Password too short! Try again.")

def register(username, password=None, min_len=6):
    # ask for password if not provided
    if password is None:
        password = prompt_password(min_len)


    # check duplicate username
    for user in data["users"]:
        if user["username"] == username:
            return False  # Username already exists

    # save user
    data["users"].append({"username": username, "password": password,"cart": []})
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)
    return True

def add_to_cart(items, cart):
    print("Available products:")
    for item in items:
        print(f"{item['id']}. {item['title']} - ${item['price']} (Stock: {item.get('stock', 'N/A')})")

    try:
        product_id = int(input("Enter the product ID to add to cart: "))
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return

    for item in items:
        if item['id'] == product_id:
            if 'stock' in item and quantity > item['stock']:
                print(f"Only {item['stock']} items available in stock.")
                return
            cart.append({"id": item['id'], "title": item['title'], "price": item['price'], "quantity": quantity})
            print(f"Added {quantity} of {item['title']} to cart.")
            return

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

def save_cart(cart):
    data["users"] = [
        {**user, "cart": cart} if user["username"] == username else user
        for user in data["users"]
    ]
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

def checkout(cart):
    if not cart:
        print("Your cart is empty.")
        return

    print("Checking out the following items:")
    total = 0
    for item in cart:
        item_total = item['price'] * item['quantity']
        total += item_total
        print(f"{item['title']} - ${item['price']} x {item['quantity']} = ${item_total:.2f}")
    print(f"Total amount due: ${total:.2f}")
    with open("receipt.txt", "a") as f:
        f.write("--- New Purchase ---\n")
        x = datetime.datetime.now()
        f.write("Order ID: " + str(random.randint(1000,9999)) + "\n")
        f.write("User: " + username + "\n")
        f.write(x.strftime("%c") + "\n")
        for item in cart:
            f.write(f"{item['title']} - ${item['price']} x {item['quantity']} = ${item['price'] * item['quantity']:.2f}\n")
    for cart_item in cart:
        for catalog_item in data["catalog"]:
            if catalog_item["id"] == cart_item["id"]:
                catalog_item["stock"] -= cart_item["quantity"]
                break
    cart.clear()
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)
    print("Thank you for your purchase!")


def menu(cart):
    while True:
        print(f"Welcome {username} to the Shop System")
        print("1.Add to cart")
        print("2.Remove from cart")
        print("3.View cart")
        print("4.Save cart")
        print("5.Checkout")
        print("6.Exit")
        print("---------------------")
        match input("Choose an option (1-6): ").strip():
            case "1":
                add_to_cart(data["catalog"], cart)
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
                save_cart(cart)
                print("Cart saved.")
                print("---------------------")
            case "5":
                print("Checking out...")
                checkout(cart)
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

                print(f"Login successful, Welcome! {username}" if login(username, password_hash) else "Invalid username or password")
                if login(username, password_hash):
                    cart = [data_user["cart"] for data_user in data["users"] if data_user["username"] == username][0]
                    menu(cart)

            case "register":
                username = input("Choose a username: ")
                password = prompt_password(6)
                print("Registration successful" if register(username, password) else "Username already exists")

            case "exit":
                print("Bye!")
                break

            case _:
                print("Invalid choice")

main()