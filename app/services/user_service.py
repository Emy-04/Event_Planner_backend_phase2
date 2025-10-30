from app.database import get_connection
from main import bcrypt

def register_user(data):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_pw))
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "User registered successfully!"}, 201
    except Exception as e:
        print("Error:", e)
        return {"error": "User already exists or database error"}, 400


def login_user(data):
    email = data.get('email')
    password = data.get('password')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and bcrypt.check_password_hash(user[0], password):
        return {"message": "Login successful!"}, 200
    else:
        return {"error": "Invalid email or password"}, 401
