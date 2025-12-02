import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="EventPlanner",     # your database name
        user="postgres",              # your PostgreSQL username
        password="mariam",# replace with your actual password
        host="db",
        port="5432"
    )