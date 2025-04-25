import sqlite3
from passlib.hash import pbkdf2_sha256

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        full_name TEXT)''')
    conn.commit()
    conn.close()

def create_user(username, password, full_name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        hashed = pbkdf2_sha256.hash(password)
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hashed, full_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result and pbkdf2_sha256.verify(password, result[0])
