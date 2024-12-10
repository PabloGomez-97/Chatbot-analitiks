import os
import time
from threading import Timer
import openai
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from twilio.rest import Client
from utils.global_state import user_state, timers, last_interaction_time


# Importaciones de utils
from utils.product_fetcher import fetch_and_save_products_json
from utils.db_helpers import (
    get_db_connection,
    save_message,
    get_user_responses,
    user_exists
)

from utils.message_formatter import (
    create_menu_message,
    handle_option_7,
    format_history,
    format_about_us,
    format_contact_info,
    format_goodbye,
    format_assistant_mode,
    format_product_search_options
)
from utils.user_handlers import handle_new_user_flow
from utils.product_handlers import handle_product_search_options, handle_specific_product_info
from controllers.openai.chat_mode import handle_assistant_mode

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def inactivity_warning(user_number):
    if user_number in last_interaction_time:
        current_time = time.time()
        if current_time - last_interaction_time[user_number] > 300:
            print(f"Despedida enviada a {user_number}")
            last_interaction_time.pop(user_number, None)
            if user_number in timers:
                timers[user_number].cancel()
                timers.pop(user_number, None)

@app.route('/update_products', methods=['GET'])
def update_products():
    fetch_and_save_products_json()
    return "✅ Datos de productos actualizados exitosamente", 200

@app.route('/getleads', methods=['GET'])
def get_recent_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE `create` >= NOW() - INTERVAL 1 DAY")
    users = cursor.fetchall()
    conn.close()
    return {"users": users}, 200

@app.route('/getusers', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return {"users": users}

@app.route('/getmessages', methods=['GET'])
def get_messages():
    # Obtener el `user_number` del cliente desde los parámetros de la solicitud
    user_number = request.args.get("user_number")

    if not user_number:
        return jsonify({"error": "El parámetro user_number es obligatorio"}), 400

    try:
        # Conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener mensajes específicos para el user_number enviados solo por el cliente
        query = """
        SELECT message, sender, timestamp 
        FROM conversations 
        WHERE user_number = %s AND sender = 'User' 
        ORDER BY timestamp DESC 
        LIMIT 6
        """
        cursor.execute(query, (user_number,))
        messages = cursor.etchall()[::-1]  # Invertir para mostrar del más antiguo al más reciente

        conn.close()

        # Si no hay mensajes registrados
        if not messages:
            return jsonify({
                "user_number": user_number,
                "history": "No hay mensajes registrados del cliente"
            }), 200

        # Formatear historial
        responses = [(msg["message"], msg["sender"], msg["timestamp"]) for msg in messages]
        user = user_exists(user_number)  # Asumimos que retorna (name, company)
        name = user[0] if user else "Cliente"  # Usar un nombre predeterminado si no existe
        company = user[1] if user else "No especificada"  # Usar una empresa predeterminada si no existe
        formatted_history = format_history(responses, name)

        # Devolver historial como JSON
        return jsonify({
            "user_number": user_number,
            "user_name": name,
            "company": company,
            "history": formatted_history
        }), 200

    except Exception as e:
        print(f"Error al obtener mensajes: {str(e)}")
        return jsonify({"error": "Hubo un problema al recuperar el historial"}), 500


@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    # Obtener detalles del mensaje entrante
    incoming_message = request.values.get('Body', '').strip().lower()
    user_number = request.values.get('From').replace('whatsapp:', '')

    # Inicializar respuesta
    response = MessagingResponse()
    last_interaction_time[user_number] = time.time()

    # Gestionar temporizador de inactividad
    if user_number in timers:
        timers[user_number].cancel()
    timers[user_number] = Timer(300, inactivity_warning, args=[user_number])
    timers[user_number].start()

    # Verificar si el usuario está en executive_mode
    if user_state.get(user_number) == 'executive_mode':
        if incoming_message == "salir":
            # Salir del modo ejecutivo
            user_state.pop(user_number, None)
            response.message("👋 Has salido de la conversación con el ejecutivo. Volviendo al menú principal...")
            response.message(create_menu_message("Cliente", "Tu empresa"))  # Cambia "Cliente" y "Tu empresa" según sea necesario
        else:
            # Permitir la conversación con el ejecutivo
            response.message()
        return str(response)

    # Verificar si el usuario está en assistant_mode
    if user_state.get(user_number) == 'assistant_mode':
        return handle_assistant_mode(user_number, incoming_message, response, user_state, "Cliente", "Tu empresa")

    # Verificar si el usuario existe
    user = user_exists(user_number)

    # Flujo para usuarios no registrados
    if not user:
        return handle_new_user_flow(user_number, incoming_message, response, user_state)

    # Manejar otros flujos
    return _handle_main_menu_flow(user_number, incoming_message, response, user)



def _handle_main_menu_flow(user_number, incoming_message, response, user):
    name, company = user  # Extraer `name` y `company` del usuario

    if incoming_message.lower() == "hola" or incoming_message not in ['1', '2', '3', '4', '5', '6', '7']:
        response.message(create_menu_message(name, company))
    else:
        if incoming_message == '1':
            response.message(format_about_us())
        elif incoming_message == '2':
            response.message(format_contact_info())
        elif incoming_message == '3':
            user_state[user_number] = 'assistant_mode'
            response.message(format_assistant_mode())
        elif incoming_message == '4':
            responses = get_user_responses(user_number)
            formatted_history = format_history(responses, name)
            response.message(formatted_history)
        elif incoming_message == '5':
            response.message(format_product_search_options())
            user_state[user_number] = 'product_search_options'
        elif incoming_message == '6':
            response.message(format_goodbye(name))
            del last_interaction_time[user_number]
            timers[user_number].cancel()
            del timers[user_number]
            user_state.pop(user_number, None)
        elif incoming_message == '7':
            return handle_option_7(user_number, response)

    # Guarda siempre todos los mensajes
    save_message(user_number, incoming_message, 'User')
    return str(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)