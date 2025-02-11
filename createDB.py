import mysql.connector

# Connection parameters (without specifying a database yet)
db_host = "database-1.crosc2qqg17q.eu-north-1.rds.amazonaws.com"
db_user = "admin"
db_password = "P*B&a33v+!7xj+*"
db_port = 3306  # MySQL default port
db_name = "my_bike_data"

# Connect to MySQL (without specifying a database)
def connect_without_db():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        port=db_port
    )

# Create database if it doesn’t exist
def create_database():
    conn = connect_without_db()
    cursor = conn.cursor()
    
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
    conn.commit()
    
    cursor.close()
    conn.close()
    print(f"✅ Database '{db_name}' checked/created successfully.")

# Run the database creation function
create_database()