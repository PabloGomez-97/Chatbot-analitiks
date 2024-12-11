from flask import Blueprint
from utils.db_helpers import get_db_connection

users_bp = Blueprint('users', __name__)

def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return {"users": users}