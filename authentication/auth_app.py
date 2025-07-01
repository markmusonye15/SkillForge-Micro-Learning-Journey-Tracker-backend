from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt

from flask_jwt_extended import JWTManager, create_access_token
import psycopg2
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Use env in production
jwt = JWTManager(app)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="your_db",
    user="postgres",
    password="your_db_password"
)
cursor = conn.cursor()

# Create users table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")
conn.commit()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "User already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()

    if result and bcrypt.check_password_hash(result[0], password):
        access_token = create_access_token(identity=email)
        return jsonify({"token": access_token}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    
   

if __name__ == "__main__":
    app.run(debug=True)
