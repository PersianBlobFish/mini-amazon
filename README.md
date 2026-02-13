# mini-amazon

## About The Project

Mini-Amazon is a console-based e-commerce application that simulates a simple online shopping experience. It provides core functionalities for user management, product browsing, shopping cart operations, and an administrative backend for managing the store.

The application persists data using a combination of JSON files for product catalog and user carts, and an SQLite database for storing hashed user credentials.

## Features

### User Features
*   **Authentication**: Secure user registration and login system. Passwords are hashed using SHA-256 hashing and stored in an SQLite database.
*   **Product Catalog**: View all available products with details like price and stock.
*   **Shopping Cart**:
    *   Add products to a personal shopping cart.
    *   Remove products from the cart.
    *   View the current contents of the cart and the total cost.
    *   Save cart contents to persist between sessions.
*   **Checkout**: Finalize a purchase. The system verifies stock, generates a receipt in `receipt.txt`, updates product stock, and clears the user's cart.

### Admin Features
An `admin` user has access to a special administrative panel with the following capabilities:
*   **View All Users**: List all registered usernames.
*   **Product Management**:
    *   View the complete product catalog with stock levels.
    *   Add new products to the catalog.
    *   Remove existing products by ID.
*   **Database Access**: A simple command-line interface to execute raw SQL queries on the `user.db` database for advanced management.

## Getting Started

To run this application, you need to have Python 3 installed on your system.

1.  Clone the repository:
    ```sh
    git clone https://github.com/persianblobfish/mini-amazon.git
    ```
2.  Navigate to the project directory:
    ```sh
    cd mini-amazon
    ```
3.  Run the main application script:
    ```sh
    python main.py
    ```
4.  Follow the on-screen prompts to either `register` a new account, `login` to an existing one, or `exit`. To access the admin panel, log in with the username `admin`.

## File Structure

*   `main.py`: The main executable script containing the application's entry point, user interface logic, and menu systems.
*   `user.py`: Defines the `User` class to model application users and their carts.
*   `product.py`: Defines the `Product` class to model items in the store.
*   `catalog.py`: Defines the `Catalog` class for managing the collection of products, including search and filtering logic.
*   `users.json`: A JSON file that stores the product catalog data and user cart information.
*   `user.db`: An SQLite database that stores user credentials (username and hashed password).
*   `receipt.txt`: A text file that logs all completed purchases with order details.