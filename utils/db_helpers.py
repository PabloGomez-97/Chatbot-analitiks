import mysql.connector

# Función para obtener una conexión a la base de datos.
# Recodemos que estamos utilizando docker, y lo que hace docker es que crea un contenedor con la base de datos.

def get_db_connection():
    return mysql.connector.connect(
        host="mysql_db",
        user="crm_user",
        password="crm_password",
        database="crm_db",
        port=3306
    )

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

def user_exists(user_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, company FROM users WHERE user_number = %s", (user_number,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def save_user(user_number, name, company):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_number, name, company) VALUES (%s, %s, %s)", (user_number, name, company))
    conn.commit()
    cursor.close()
    conn.close()
