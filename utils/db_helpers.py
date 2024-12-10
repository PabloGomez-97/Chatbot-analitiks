import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", # es lo único que hay que modificar cuando subimos a la EC2
        user="crm_user",
        password="crm_password",
        database="crm_db",
        port=3306
    )

                """ Es utilizado en -> controllers/openai/chat_mode.py """
                """ Es utilizado en -> utils/product_handler.py """
def save_message(user_number, message, sender):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (user_number, message, sender) VALUES (%s, %s, %s)", (user_number, message, sender))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_responses(user_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT message, sender, timestamp FROM conversations WHERE user_number = %s ORDER BY timestamp", (user_number,))
    responses = cursor.fetchall()
    cursor.close()
    conn.close()
    return responses

                """ Es utilizado en -> controllers/openai/openai.py """
def user_exists(user_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, company FROM users WHERE user_number = %s", (user_number,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

                """ Es utilizado en -> utils/user_handlers.py """
def save_user(user_number, name, company):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_number, name, company) VALUES (%s, %s, %s)", (user_number, name, company))
    conn.commit()
    cursor.close()
    conn.close()
