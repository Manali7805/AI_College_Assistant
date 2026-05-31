import sqlite3

# ==========================================================
# DATABASE CONNECTION
# ==========================================================

conn = sqlite3.connect("college_assistant.db", check_same_thread=False)

cursor = conn.cursor()

# ==========================================================
# CREATE USERS TABLE
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()

# ==========================================================
# REGISTER USER
# ==========================================================

def register_user(name, email, password):

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )

        conn.commit()

        return True

    except:
        return False

# ==========================================================
# LOGIN USER
# ==========================================================

def login_user(email, password):

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()

    return user