from app.database import get_connection
from app import bcrypt
from flask_jwt_extended import create_access_token

def register_user(data):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s) RETURNING id",
            (email, hashed_pw)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "User registered successfully!", "user_id": user_id}, 201
    except Exception as e:
        print("Error:", e)
        return {"error": "User already exists or database error"}, 400


def login_user(data):
    email = data.get('email')
    password = data.get('password')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and bcrypt.check_password_hash(user[1], password):
        # Use string ID as identity to avoid "Subject must be a string"
        token = create_access_token(identity=str(user[0]))
        return {"message": "Login successful!", "access_token": token}, 200
    else:
        return {"error": "Invalid email or password"}, 401
