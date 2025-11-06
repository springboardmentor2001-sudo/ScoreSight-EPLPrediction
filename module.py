from database import get_db_connection
import hashlib
from datetime import datetime, timedelta

# -------------------------------
# Helper functions for users
# -------------------------------

def hash_password(password):
    """Hash the password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------------
# Table creation functions
# -------------------------------

def create_users_table():
    """Create the users table if it doesn't exist"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    mobile VARCHAR(15) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
    finally:
        conn.close()


def create_logs_table():
    """Create a table for logging all user activities (page visits, actions, etc.)"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_logs (
                    log_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_email VARCHAR(100),
                    page_name VARCHAR(100),
                    activity VARCHAR(255),
                    ip_address VARCHAR(50),
                    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
    finally:
        conn.close()

# -------------------------------
# Logging Function
# -------------------------------

def log_user_activity(email, activity, page_name=None, ip_address=None):
    """
    Save user activity (including page visits) into the logs table.
    Also auto-deletes logs older than 30 days.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Insert new log entry
            sql_insert = """
                INSERT INTO user_logs (user_email, page_name, activity, ip_address, log_time)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (email, page_name, activity, ip_address, datetime.now()))

            # Delete logs older than 30 days
            sql_delete_old = "DELETE FROM user_logs WHERE log_time < %s"
            thirty_days_ago = datetime.now() - timedelta(days=30)
            cursor.execute(sql_delete_old, (thirty_days_ago,))
        conn.commit()
    finally:
        conn.close()

# -------------------------------
# User Functions
# -------------------------------

def register_user(first_name, last_name, email, mobile, password):
    """Register a new user in the database"""
    conn = get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            sql_check = "SELECT * FROM users WHERE email=%s"
            cursor.execute(sql_check, (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                log_user_activity(email, "Failed Registration (Email Exists)", page_name="register")
                return False, "Email already registered"

            hashed_pw = hash_password(password)
            sql_insert = """
                INSERT INTO users (first_name, last_name, email, mobile, password)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (first_name, last_name, email, mobile, hashed_pw))
            conn.commit()

            log_user_activity(email, "User Registered Successfully", page_name="register")
            return True, "User registered successfully"
    finally:
        conn.close()


def verify_user(email, password):
    """Verify login credentials"""
    conn = get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM users WHERE email=%s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user and user["password"] == hash_password(password):
                log_user_activity(email, "Login Successful", page_name="login")
                return True, user
            else:
                log_user_activity(email, "Login Failed (Wrong Credentials)", page_name="login")
                return False, None
    finally:
        conn.close()

# -------------------------------
# Initialize tables (run once)
# -------------------------------

def setup_database():
    create_users_table()
    create_logs_table()
