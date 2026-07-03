import os
import sqlite3
import secrets
import string
from flask import Flask, render_template, request, redirect, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
#It is important to notee that the secret should be kept secret.
app = Flask(__name__)
app.secret_key = "change-this-secret-key-later"

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

csrf = CSRFProtect(app)

DB_NAME = "password_manager.db"
KEY_FILE = "secret.key"

# Load or create encryption key.
def load_or_create_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)

    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

# Initialize the Fernet cipher with the loaded or created key.
cipher = Fernet(load_or_create_key())


def encrypt_text(text):
    return cipher.encrypt(text.encode()).decode()


def decrypt_text(encrypted_text):
    return cipher.decrypt(encrypted_text.encode()).decode()


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
# Initialize the database and create tables if they don't exist.

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            website TEXT NOT NULL,
            account_username TEXT NOT NULL,
            encrypted_password TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()

# Routes
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")

        flash("Invalid username or password.")
        return redirect("/login")

    return render_template("login.html")

# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if len(username) < 3:
            flash("Username must be at least 3 characters.")
            return redirect("/register")

        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            return redirect("/register")

        password_hash = generate_password_hash(password)

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            conn.close()

            flash("Account created successfully. Please login.")
            return redirect("/login")

        except sqlite3.IntegrityError:
            flash("Username already exists.")
            return redirect("/register")

    return render_template("register.html")

# Dashboard route
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM credentials WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()
# Decrypt the passwords before sending them to the template.
    credentials = []
    for row in rows:
        credentials.append({
            "id": row["id"],
            "website": row["website"],
            "account_username": row["account_username"],
            "password": decrypt_text(row["encrypted_password"]),
            "notes": row["notes"]
        })

    return render_template(
        "dashboard.html",
        username=session["username"],
        credentials=credentials
    )

# Add credential route
@app.route("/add", methods=["POST"])
def add_credential():
    if "user_id" not in session:
        return redirect("/login")

    website = request.form["website"].strip()
    account_username = request.form["account_username"].strip()
    password = request.form["password"]
    notes = request.form["notes"].strip()

    if not website or not account_username or not password:
        flash("Website, username, and password are required.")
        return redirect("/dashboard")

    encrypted_password = encrypt_text(password)

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO credentials
        (user_id, website, account_username, encrypted_password, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session["user_id"], website, account_username, encrypted_password, notes)
    )
    conn.commit()
    conn.close()

    flash("Credential saved securely.")
    return redirect("/dashboard")


@app.route("/delete/<int:credential_id>", methods=["POST"])
def delete_credential(credential_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    conn.execute(
        "DELETE FROM credentials WHERE id = ? AND user_id = ?",
        (credential_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    flash("Credential deleted.")
    return redirect("/dashboard")


@app.route("/generate-password")
def generate_password():
    if "user_id" not in session:
        return redirect("/login")

    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    generated_password = "".join(secrets.choice(characters) for _ in range(16))

    flash(f"Generated password: {generated_password}")
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)