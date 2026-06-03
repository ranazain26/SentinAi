import hashlib
import pickle
import subprocess
import os
import random
import sqlite3

# Hardcoded credentials - BAD PRACTICE
password = "admin123"
api_key = "sk-abc123secretkeyhere456789"
database_url = "postgresql://admin:password123@localhost/mydb"

def login(username, user_password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # SQL INJECTION VULNERABILITY
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

def hash_password(pw):
    # WEAK HASHING - MD5 is broken
    return hashlib.md5(pw.encode()).hexdigest()

def run_command(user_input):
    # COMMAND INJECTION
    os.system("ls " + user_input)
    subprocess.call("echo " + user_input, shell=True)

def load_data(data):
    # UNSAFE DESERIALIZATION
    return pickle.loads(data)

def get_token():
    # WEAK RANDOM
    return random.randint(100000, 999999)

def read_file(filename):
    # PATH TRAVERSAL
    with open("/var/data/" + filename) as f:
        return f.read()

debug = True  # DEBUG MODE IN CODE

# TODO: Fix all the security issues above
# FIXME: This function is broken
def broken_function():
    pass

def divide(a, b):
    return a / b  # No zero check

def bad_defaults(items=[]):  # Mutable default argument
    items.append(1)
    return items