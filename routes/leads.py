from flask import Blueprint
from utils.dbhelpers import get_db_connection

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('/getleads', methods=['GET'])
def get_recent_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE `create` >= NOW() - INTERVAL 1 DAY")
    users = cursor.fetchall()
    conn.close()
    return {"users": users}, 200
