"""Create and populate the SQLite database used by the text-to-SQL app."""

from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from random import Random

DB_PATH = Path(__file__).resolve().parent / "ecommerce.db"


def create_tables(connection: sqlite3.Connection) -> None:
    """Drop and recreate all SQLite tables used by the app."""
    connection.executescript(
        """
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            country TEXT,
            signup_date TEXT
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            price REAL
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(customer_id),
            order_date TEXT,
            status TEXT
        );

        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER REFERENCES orders(order_id),
            product_id INTEGER REFERENCES products(product_id),
            quantity INTEGER,
            unit_price REAL
        );
        """
    )


def insert_customers(connection: sqlite3.Connection) -> None:
    """Insert 15 realistic customers."""
    customers = [
        (1, "Aarav", "Sharma", "aarav.sharma@example.com", "India", "2025-01-12"),
        (2, "Emma", "Wilson", "emma.wilson@example.com", "USA", "2025-02-03"),
        (3, "Liam", "Brown", "liam.brown@example.com", "UK", "2025-02-18"),
        (4, "Olivia", "Martin", "olivia.martin@example.com", "France", "2025-03-02"),
        (5, "Noah", "Taylor", "noah.taylor@example.com", "Canada", "2025-03-21"),
        (6, "Diya", "Patel", "diya.patel@example.com", "India", "2025-04-07"),
        (7, "Lucas", "Anderson", "lucas.anderson@example.com", "USA", "2025-04-19"),
        (8, "Sophia", "Clark", "sophia.clark@example.com", "Australia", "2025-05-11"),
        (9, "Ethan", "Thomas", "ethan.thomas@example.com", "UK", "2025-05-29"),
        (10, "Mia", "Walker", "mia.walker@example.com", "Germany", "2025-06-14"),
        (11, "Arjun", "Verma", "arjun.verma@example.com", "India", "2025-07-28"),
        (12, "Isabella", "Moore", "isabella.moore@example.com", "USA", "2025-08-09"),
        (13, "James", "White", "james.white@example.com", "Canada", "2025-09-22"),
        (14, "Ananya", "Singh", "ananya.singh@example.com", "India", "2025-10-05"),
        (15, "Henry", "Harris", "henry.harris@example.com", "UK", "2025-11-20"),
    ]
    connection.executemany(
        "INSERT INTO customers (customer_id, first_name, last_name, email, country, signup_date) VALUES (?, ?, ?, ?, ?, ?)",
        customers,
    )


def insert_products(connection: sqlite3.Connection) -> None:
    """Insert 10 products across multiple categories."""
    products = [
        (1, "Wireless Headphones", "Electronics", 79.99),
        (2, "Mechanical Keyboard", "Electronics", 119.99),
        (3, "USB-C Hub", "Electronics", 39.99),
        (4, "Running Shoes", "Sports", 89.99),
        (5, "Yoga Mat", "Sports", 29.99),
        (6, "Coffee Maker", "Home", 64.99),
        (7, "Desk Lamp", "Home", 34.99),
        (8, "Backpack", "Accessories", 54.99),
        (9, "Water Bottle", "Accessories", 19.99),
        (10, "Smart Watch", "Electronics", 149.99),
    ]
    connection.executemany(
        "INSERT INTO products (product_id, product_name, category, price) VALUES (?, ?, ?, ?)",
        products,
    )


def insert_orders(connection: sqlite3.Connection) -> None:
    """Insert 30 orders spread across the last 12 months."""
    rng = Random(42)
    today = date.today()
    statuses = ["completed", "pending", "cancelled"]
    orders: list[tuple[int, int, str, str]] = []

    for order_id in range(1, 31):
        customer_id = rng.randint(1, 15)
        days_ago = rng.randint(0, 364)
        order_date = today - timedelta(days=days_ago)
        status = rng.choice(statuses)
        orders.append((order_id, customer_id, order_date.isoformat(), status))

    connection.executemany(
        "INSERT INTO orders (order_id, customer_id, order_date, status) VALUES (?, ?, ?, ?)",
        orders,
    )


def insert_order_items(connection: sqlite3.Connection) -> None:
    """Insert 1-4 items per order using the product price at insert time."""
    rng = Random(42)
    products = connection.execute(
        "SELECT product_id, price FROM products ORDER BY product_id"
    ).fetchall()

    order_items: list[tuple[int, int, int, int, float]] = []
    order_item_id = 1

    for order_id in range(1, 31):
        item_count = rng.randint(1, 4)
        selected_products = rng.sample(products, item_count)

        for product_id, price in selected_products:
            quantity = rng.randint(1, 3)
            order_items.append((order_item_id, order_id, product_id, quantity, float(price)))
            order_item_id += 1

    connection.executemany(
        "INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
        order_items,
    )


def print_summary(connection: sqlite3.Connection) -> None:
    """Print a short row-count summary for each table."""
    print("\nDatabase created successfully.")
    print(f"Database path: {DB_PATH}\n")

    for table_name in ["customers", "products", "orders", "order_items"]:
        count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"{table_name}: {count} rows")


def main() -> None:
    """Rebuild the SQLite database from scratch and print a summary."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        create_tables(connection)
        insert_customers(connection)
        insert_products(connection)
        insert_orders(connection)
        insert_order_items(connection)
        connection.commit()
        print_summary(connection)


if __name__ == "__main__":
    main()
