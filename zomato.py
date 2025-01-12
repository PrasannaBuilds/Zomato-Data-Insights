import streamlit as st
import psycopg2
from psycopg2 import sql
from faker import Faker
import pandas as pd
import random
from streamlit_lottie import st_lottie
import requests

faker = Faker()

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return None
    
# PostgreSQL connection details
DB_HOST = "localhost"
DB_NAME = "zomato_db"
DB_USER = "postgres"
DB_PASSWORD = "admin"

class DatabaseConnection:
    @staticmethod
    def connect():
        try:
            conn = psycopg2.connect(
                host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
            )
            return conn
        except Exception as e:
            st.error(f"Error connecting to database: {e}")
            return None

class TableManager:
    @staticmethod
    def create_tables(conn):
        commands = [
            """CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(15),
                location VARCHAR(200),
                signup_date DATE,
                is_premium BOOLEAN,
                preferred_cuisine VARCHAR(50),
                total_orders INT,
                average_rating FLOAT
            )""",
            """CREATE TABLE IF NOT EXISTS restaurants (
                restaurant_id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                cuisine_type VARCHAR(50),
                location VARCHAR(200),
                owner_name VARCHAR(100),
                average_delivery_time INT,
                contact_number VARCHAR(15),
                rating FLOAT,
                total_orders INT,
                is_active BOOLEAN DEFAULT TRUE
            )""",
            """CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INT REFERENCES customers(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
                restaurant_id INT REFERENCES restaurants(restaurant_id) ON DELETE CASCADE ON UPDATE CASCADE,
                order_date TIMESTAMP,
                delivery_time TIMESTAMP,
                status VARCHAR(20),
                total_amount FLOAT,
                payment_mode VARCHAR(50),
                discount_applied FLOAT,
                feedback_rating FLOAT
            )""",
            """CREATE TABLE IF NOT EXISTS deliveries (
                delivery_id SERIAL PRIMARY KEY,
                order_id INT REFERENCES orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
                delivery_status VARCHAR(50),
                distance FLOAT,
                delivery_time INT,
                estimated_time INT,
                delivery_fee FLOAT,
                vehicle_type VARCHAR(50)
            )"""
        ]
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()

class DataGenerator:
    @staticmethod
    def generate_data(conn):
        cur = conn.cursor()
        customer_ids = []
        restaurant_ids = []

        for _ in range(10):
            cur.execute(
                """
                INSERT INTO customers (name, email, phone, location, signup_date, is_premium, preferred_cuisine, total_orders, average_rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING customer_id
                """,
                (
                    faker.name()[:50],
                    faker.email()[:100],
                    faker.phone_number()[:15],
                    faker.address()[:200],
                    faker.date_this_decade(),
                    random.choice([True, False]),
                    random.choice(["Indian", "Chinese", "Italian", "Mexican"]),
                    random.randint(0, 100),
                    round(random.uniform(1, 5), 2)
                ),
            )
            customer_ids.append(cur.fetchone()[0])

        for _ in range(20):
            cur.execute(
                """
                INSERT INTO restaurants (name, cuisine_type, location, owner_name, average_delivery_time, contact_number, rating, total_orders, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING restaurant_id
                """,
                (
                    faker.company()[:100],
                    random.choice(["Indian", "Chinese", "Italian", "Mexican"]),
                    faker.address()[:200],
                    faker.name()[:100],
                    random.randint(20, 60),
                    faker.phone_number()[:15],
                    round(random.uniform(1, 5), 1),
                    random.randint(0, 1000),
                    random.choice([True, False])
                ),
            )
            restaurant_ids.append(cur.fetchone()[0])

        for _ in range(20):
            cur.execute(
                """
                INSERT INTO orders (
                    customer_id, restaurant_id, order_date, delivery_time, status, total_amount, payment_mode, discount_applied, feedback_rating
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    random.choice(customer_ids),
                    random.choice(restaurant_ids),
                    faker.date_time_this_year(),
                    faker.date_time_this_year(),
                    random.choice(["Pending", "Completed", "Cancelled"]),
                    random.uniform(10.0, 200.0),
                    random.choice(["Cash", "Card", "Online"]),
                    random.uniform(0, 20),
                    random.randint(1, 5)
                ),
            )

        cur.execute("SELECT order_id FROM orders")
        order_ids = [row[0] for row in cur.fetchall()]
        for _ in range(20):
            cur.execute(
                """
                INSERT INTO deliveries 
                (order_id, delivery_status, distance, delivery_time, estimated_time, delivery_fee, vehicle_type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    random.choice(order_ids),
                    random.choice(["Pending", "Completed", "Cancelled"]),
                    random.uniform(1.0, 50.0),
                    random.randint(10, 60),
                    random.randint(10, 60),
                    random.uniform(5.0, 50.0),
                    random.choice(["Car", "Bike", "Truck"]),
                ),
            )

        conn.commit()
        cur.close()

class DataHandler:
    @staticmethod
    def get_tables(conn):
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        return tables

    @staticmethod
    def get_columns(conn, table):
        cur = conn.cursor()
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position;")
        columns = [row[0] for row in cur.fetchall()]
        cur.close()
        return columns

    @staticmethod
    def dynamic_read(conn, table):
        columns = DataHandler.get_columns(conn, table)
        cur = conn.cursor()
        cur.execute(f"SELECT {', '.join(columns)} FROM {table}")
        rows = cur.fetchall()
        cur.close()
        return rows, columns

    @staticmethod
    def dynamic_insert(conn, table, values):
        cur = conn.cursor()
        columns = DataHandler.get_columns(conn, table)
        placeholders = ", ".join(["%s"] * len(values))
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(placeholders)
        )
        cur.execute(query, values)
        conn.commit()
        cur.close()

    # Update existing values dynamically in a table
    @staticmethod
    def dynamic_update(conn, table, primary_key_column, primary_key_value, column_to_update, new_value):
        cur = conn.cursor()
        query = sql.SQL("UPDATE {} SET {} = %s WHERE {} = %s").format(
            sql.Identifier(table),
            sql.Identifier(column_to_update),
            sql.Identifier(primary_key_column)
        )
        cur.execute(query, [new_value, primary_key_value])
        conn.commit()
        cur.close()

    # Delete a record dynamically
    @staticmethod
    def dynamic_delete(conn, table, primary_key_column, primary_key_value):
        try:
            with conn.cursor() as cur:
                if table == "customers":
                    cur.execute("""
                        DELETE FROM deliveries 
                        WHERE order_id IN (SELECT order_id FROM orders WHERE customer_id = %s)
                    """, (primary_key_value,))
                    cur.execute("DELETE FROM orders WHERE customer_id = %s", (primary_key_value,))

                elif table == "orders":
                    cur.execute("DELETE FROM deliveries WHERE order_id = %s", (primary_key_value,))
                    cur.execute(sql.SQL("DELETE FROM {} WHERE {} = %s").format(
                    sql.Identifier(table),
                    sql.Identifier(primary_key_column)
                ), [primary_key_value])

                conn.commit()
                st.success(f"Record deleted successfully from {table}!")
        except psycopg2.errors.ForeignKeyViolation as e:
            st.error(f"Foreign key violation: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

class QueryExecutor:
    @staticmethod
    def execute_query(conn, query):
        try:
            cur = conn.cursor()
            cur.execute(query)
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            cur.close()
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return None

class Application:
    def __init__(self):
        self.conn = DatabaseConnection.connect()
        if self.conn:
            TableManager.create_tables(self.conn)

    @staticmethod
    def load_lottie_url(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.warning(f"Error loading animation: {e}")
        return None

    def run(self):
        if not self.conn:
            st.error("Database connection could not be established.")
            return

        #Header
        st.set_page_config(page_title="Zomato Data Insights", page_icon="🍴", layout="wide")
        st.title("🍴 Zomato Data Insights")

        #Menu
        menu = ["Home", "Add Data", "Manage Data", "Data Analysis"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Home":
            st.subheader("Welcome to Zomato Data Management System!")
            st.write("Use the navigation menu on the left to explore different sections of the application.")
            lottie_animation = self.load_lottie_url("https://assets3.lottiefiles.com/packages/lf20_3rwasyjy.json")
            if lottie_animation:
                st_lottie(lottie_animation, speed=1, height=300, key="home-animation")

        elif choice == "Add Data":
            st.subheader("Add Data to the Database")
            st.info("Click the button below to generate and add sample data to the database.")
            if st.button("Generate Data"):
                DataGenerator.generate_data(self.conn)
                st.success("Sample data has been successfully added to the database!")

        elif choice == "Manage Data":
            st.subheader("Manage Data")
            tables = DataHandler.get_tables(self.conn)
            if tables:
                selected_table = st.selectbox("Select a Table to Manage", tables)
                operation = st.selectbox("Select Operation", ["View Data", "Insert Data", "Update Data", "Delete Data"])

                if operation == "View Data":
                    st.subheader(f"View Data in {selected_table}")
                    if st.button("Load Data"):
                        data, columns = DataHandler.dynamic_read(self.conn, selected_table)
                        if data:
                            st.dataframe(pd.DataFrame(data, columns=columns))
                        else:
                            st.warning(f"No data available in {selected_table}.")

                elif operation == "Insert Data":
                    st.subheader(f"Insert New Data into {selected_table}")
                    columns = DataHandler.get_columns(self.conn, selected_table)
                    values = [st.text_input(f"Value for {col}") for col in columns]
                    if st.button("Insert Data"):
                        DataHandler.dynamic_insert(self.conn, selected_table, values)
                        st.success("Data inserted successfully!")

                elif operation == "Update Data":
                    st.subheader(f"Update Data in {selected_table}")
                    columns = DataHandler.get_columns(self.conn, selected_table)
                    primary_key = columns[0]
                    primary_key_value = st.text_input(f"Primary Key ({primary_key}) Value")
                    column_to_update = st.selectbox("Column to Update", columns[1:])
                    new_value = st.text_input(f"New Value for {column_to_update}")
                    if st.button("Update Record"):
                        DataHandler.dynamic_update(self.conn, selected_table, primary_key, primary_key_value, column_to_update, new_value)
                        st.success("Record updated successfully!")

                elif operation == "Delete Data":
                    st.subheader(f"Delete Data from {selected_table}")
                    columns = DataHandler.get_columns(self.conn, selected_table)
                    primary_key = columns[0]
                    primary_key_value = st.text_input(f"Enter {primary_key} of the Record to Delete")
                    if st.button("Delete Record"):
                        DataHandler.dynamic_delete(self.conn, selected_table, primary_key, primary_key_value)
                        st.success("Record deleted successfully!")

        elif choice == "Data Analysis":
            st.subheader("Perform Data Analysis")
            predefined_queries = {
                "1. Peak Ordering Dates": 
                    "SELECT DATE(order_date), COUNT(*) as total_orders FROM orders GROUP BY DATE(order_date) ORDER BY total_orders DESC LIMIT 5;",
                
                "2. Delayed and Cancelled Deliveries": 
                    "SELECT order_id, delivery_status FROM deliveries WHERE delivery_status IN ('Delayed', 'Cancelled');",

                "3. Customer Preferences and Order Patterns": 
                    "SELECT preferred_cuisine, COUNT(*) as total_customers FROM customers GROUP BY preferred_cuisine ORDER BY total_customers DESC;",

                "4. Top Customers by Order Frequency":
                    "SELECT customers.customer_id, customers.name, COUNT(orders.order_id) as order_count "
                    "FROM orders "
                    "JOIN customers ON orders.customer_id = customers.customer_id "
                    "GROUP BY customers.customer_id, customers.name "
                    "ORDER BY order_count DESC "
                    "LIMIT 5;",

                "5. Top Customers by Order Value":
                    "SELECT customers.customer_id, customers.name, SUM(orders.total_amount) as total_spent "
                    "FROM orders "
                    "JOIN customers ON orders.customer_id = customers.customer_id "
                    "GROUP BY customers.customer_id, customers.name "
                    "ORDER BY total_spent DESC "
                    "LIMIT 5;",

                "6. Delivery Times and Delays":
                    "SELECT order_id, (delivery_time - order_date) AS delivery_duration FROM orders ORDER BY delivery_duration DESC LIMIT 5;",

                "7. Delivery Personnel Performance":
                    "SELECT delivery_id, delivery_status, distance, delivery_fee FROM deliveries ORDER BY delivery_fee DESC LIMIT 5;",

                "8. Most Popular Restaurants":
                    "SELECT name, total_orders FROM restaurants ORDER BY total_orders DESC LIMIT 5;",

            "9. Order Frequency by Restaurant":
                "SELECT restaurants.restaurant_id, restaurants.name, COUNT(orders.order_id) as order_count "
                "FROM orders "
                "JOIN restaurants ON orders.restaurant_id = restaurants.restaurant_id "
                "GROUP BY restaurants.restaurant_id, restaurants.name "
                "ORDER BY order_count DESC;",

                "10. Average Rating by Restaurant":
                    "SELECT name, AVG(rating) FROM restaurants GROUP BY name ORDER BY AVG(rating) DESC;",

                "11. Most Common Payment Modes":
                    "SELECT payment_mode, COUNT(*) FROM orders GROUP BY payment_mode ORDER BY COUNT(*) DESC;",

                "12. Average Order Value":
                    "SELECT AVG(total_amount) as avg_order_value FROM orders;",

                "13. Top Premium Customers":
                    "SELECT name FROM customers WHERE is_premium = TRUE;",

                "14. Restaurants with Fastest Delivery Time":
                    "SELECT name, average_delivery_time FROM restaurants ORDER BY average_delivery_time ASC LIMIT 5;",

                "15. Total Revenue Generated":
                    "SELECT SUM(total_amount) FROM orders;",

                "16. Total Deliveries Completed":
                    "SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'Completed';",

                "17. Average Feedback Rating":
                    "SELECT AVG(feedback_rating) FROM orders;",

                "18. Total Canceled Orders":
                    "SELECT COUNT(*) FROM orders WHERE status = 'Cancelled';",

                "19. Highest Delivery Fee Collected":
                    "SELECT MAX(delivery_fee) FROM deliveries;",

                "20. Most Active Restaurants":
                    "SELECT name FROM restaurants WHERE is_active = TRUE;"
            }
            query_name = st.selectbox("Select a Predefined Query", list(predefined_queries.keys()))
            if st.button("Run Query"):
                query = predefined_queries[query_name]
                result_df = QueryExecutor.execute_query(self.conn, query)
                if result_df is not None:
                    st.dataframe(result_df)
                else:
                    st.warning("No results found for the selected query.")

        self.conn.close()


if __name__ == "__main__":
    app = Application()
    app.run()
