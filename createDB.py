import mysql.connector

# RDS Database Connection Details
db_host = "database-1.cv4842ms2b5l.eu-north-1.rds.amazonaws.com"
db_name = "my_bike_data"
db_user = "admin"
db_password = "P*B&a33v+!7xj+*"
db_port = "3306"
ssl_ca = "eu-north-1-bundle.pem"

# Connect to MySQL Server
def connect_to_server():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        port=db_port,
        ssl_ca=ssl_ca,
        ssl_disabled=False
    )

# Connect to Database
def connect_to_db():
    return mysql.connector.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port,
        ssl_ca=ssl_ca,
        ssl_disabled=False
    )

# Create Database
def create_database():
    conn = connect_to_server()
    cursor = conn.cursor()
    
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    
    cursor.close()
    conn.close()
    print(f"Database '{db_name}' created or already exists.")

# Create Tables
def create_tables():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Create 'stations' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stations (
            station_id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address VARCHAR(255),
            latitude DECIMAL(9,6),
            longitude DECIMAL(9,6),
            banking BOOLEAN,
            bonus BOOLEAN,
            bike_stands INT
        )
    """)

    # Create 'station_history' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS station_history (
            history_id INT AUTO_INCREMENT PRIMARY KEY,
            station_id INT,
            name VARCHAR(255) NOT NULL,
            banking BOOLEAN,
            status VARCHAR(50),
            available_bikes INT,
            available_stands INT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (station_id) REFERENCES stations(station_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tables 'stations' and 'station_history' created or already exist.")

# Run the script
if __name__ == "__main__":
    create_database()
    create_tables()
