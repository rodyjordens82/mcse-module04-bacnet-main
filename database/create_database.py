import mysql.connector
import pyotp
from flask_bcrypt import generate_password_hash, check_password_hash

# Connect to MySQL database
conn = mysql.connector.connect(
    host="172.20.2.100",
    user="beheer",
    password="Geheim123!",
    database="db"
)
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS camera (
        id INT AUTO_INCREMENT PRIMARY KEY, 
        status FLOAT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS fire (
        id INT AUTO_INCREMENT PRIMARY KEY,
        status FLOAT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS light (
        id INT AUTO_INCREMENT PRIMARY KEY,
        status FLOAT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS locking (
        id INT AUTO_INCREMENT PRIMARY KEY,
        status FLOAT
    )
''')


# Add a default value of 1.0 to each table
default_status = 1.0

cursor.execute("INSERT INTO camera (status) VALUES (%s)", (default_status,))
cursor.execute("INSERT INTO fire (status) VALUES (%s)", (default_status,))
cursor.execute("INSERT INTO light (status) VALUES (%s)", (default_status,))
cursor.execute("INSERT INTO locking (status) VALUES (%s)", (default_status,))

# Add an MFA key for the admin account
admin_username = "admin"
admin_password = "admin"  # No more credentials in .txt
hashed_admin_password = generate_password_hash(admin_password).decode('utf-8')
admin_secret_key = pyotp.random_base32()

# Store admin information in the database
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), secret_key VARCHAR(255), role VARCHAR(255))")
cursor.execute("INSERT INTO users (username, password, secret_key, role) VALUES (%s, %s, %s, %s)",
               (admin_username, hashed_admin_password, admin_secret_key, 'admin'))

# Add an MFA key for the admin account
user_username = "user"
user_password = "user"  # No more credentials in .txt
hashed_user_password = generate_password_hash(user_password).decode('utf-8')
user_secret_key = pyotp.random_base32()

# Store admin information in the database
cursor.execute("INSERT INTO users (username, password, secret_key, role) VALUES (%s, %s, %s, %s)",
               (user_username, hashed_user_password, user_secret_key, 'user'))

# Commit and close the database connection
conn.commit()
conn.close()
