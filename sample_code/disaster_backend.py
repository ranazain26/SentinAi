import sqlite3
import hashlib
import pickle
import subprocess
import os

db_password = "super_secret_db_password_123!"

def process_user_data(user_input, session_data=[]):
    # BUG: Mutable Default Argument (session_data=[])
    session_data.append(user_input)
    
    # VULNERABILITY: Unsafe Deserialization (CWE-502)
    try:
        user_obj = pickle.loads(user_input)
    except Exception as e:
        print(e)
        return False

    return True

def authenticate_user(username, password):
    # VULNERABILITY: Weak Hashing (CWE-327)
    hashed_pw = hashlib.md5(password.encode()).hexdigest()
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # VULNERABILITY: SQL Injection (CWE-89)
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + hashed_pw + "'"
    cursor.execute(query)
    
    return cursor.fetchone()

def backup_database(backup_name):
    # VULNERABILITY: Command Injection (CWE-78)
    # shell=True combined with string concatenation
    command = "cp users.db /backups/" + backup_name
    subprocess.call(command, shell=True)
    return True

def read_log_file(filename):
    # VULNERABILITY: Path Traversal (CWE-22)
    with open(f"/var/log/app/{filename}") as f:
        return f.read()

if __name__ == "__main__":
    print("Backend server started.")