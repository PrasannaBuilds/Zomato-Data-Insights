# Zomato Data Management System
This project is a comprehensive data management and analytics application for Zomato using Streamlit and PostgreSQL. It allows users to create, manage, and analyze data related to customers, restaurants, orders, and deliveries in an interactive web-based dashboard.

## Features
- **Streamlit Web App:** User-friendly web interface for data management and analysis.
- **PostgreSQL Integration:** Full CRUD operations for customers, restaurants, orders, and deliveries.
- **OOP Design:** Modular object-oriented programming design for database and app management.
- **Data Generation:** Automated sample data generation using the `Faker` library.
- **Data Management:** Dynamic insertion, updating, and deletion of records.
- **Data Analysis:** Predefined SQL queries for business insights like peak ordering dates, customer preferences, and delivery performance.
- **Lottie Animations:** Interactive visuals for enhanced UI experience.

## Project Structure
- `DatabaseConnection`: Handles the database connection setup.
- `TableManager`: Manages the creation of tables.
- `DataGenerator`: Generates sample data for the database.
- `DataHandler`: Provides dynamic CRUD operations.
- `QueryExecutor`: Executes predefined and custom SQL queries.
- `Application`: The main Streamlit app integrating all components.

## Technologies Used
- **Python**
- **Streamlit**
- **PostgreSQL**
- **Faker Library**
- **psycopg2**
- **pandas**

## Database Schema

The database consists of the following tables:
1. customers: Manages customer data including personal details, preferences, and order history.
2. restaurants: Stores restaurant data such as cuisine type, location, and performance metrics.
3. orders: Captures order transactions, including payment details and feedback ratings.
4. deliveries: Logs delivery details like delivery time, distance, and status.

## Setup Instructions
1. **Clone the repository:**
    ```git clone <repository-url>```

2. **Navigate to the project directory:**
    ```cd zomato_data_management```

3. **Create a virtual environment:**
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. **Install the dependencies:**
    ```pip install -r requirements.txt```

5. **Setup PostgreSQL Database:**
   - Ensure PostgreSQL is installed and running.
   - Create a database named `zomato_db`.
   - Update the database credentials in the `DB_HOST`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` variables within the `Application` class.

6. **Run the Streamlit App:**
    ```streamlit run main.py```

## Usage
1. **Home Page:** Introduction and animations.
2. **Add Data:** Generate sample data for the database.
3. **Manage Data:** View, insert, update, and delete data dynamically.
4. **Data Analysis:** Run predefined queries for business insights.

## Example Predefined Queries
- Peak Ordering Dates
- Delayed and Cancelled Deliveries
- Customer Preferences
- Top Customers by Order Value

## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.


