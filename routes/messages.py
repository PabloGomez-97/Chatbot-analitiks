from flask import Blueprint, request, jsonify
from utils.db_helpers import get_db_connection, user_exists
from utils.message_formatter import format_history

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/getmessages', methods=['GET']) # Debe estar presente para que funcionen los correos
def get_messages():
    user_number = request.args.get("user_number")

    if not user_number:
        return jsonify({"error": "El parámetro user_number es obligatorio"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT message, sender, timestamp 
        FROM conversations 
        WHERE user_number = %s AND sender = 'User' 
        ORDER BY timestamp DESC 
        LIMIT 6
        """
        cursor.execute(query, (user_number,))
        messages = cursor.fetchall()[::-1]

        conn.close()

        if not messages:
            return jsonify({
                "user_number": user_number,
                "history": "No hay mensajes registrados del cliente"
            }), 200

        responses = [(msg["message"], msg["sender"], msg["timestamp"]) for msg in messages]
        user = user_exists(user_number)
        name = user[0] if user else "Cliente"
        company = user[1] if user else "No especificada"
        formatted_history = format_history(responses, name)

        return jsonify({
            "user_number": user_number,
            "user_name": name,
            "company": company,
            "history": formatted_history
        }), 200

    except Exception as e:
        print(f"Error al obtener mensajes: {str(e)}")
        return jsonify({"error": "Hubo un problema al recuperar el historial"}), 500
