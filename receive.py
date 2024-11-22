import os
import time
from threading import Timer

import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

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
    format_history,
    format_about_us,
    format_contact_info,
    format_goodbye,
    format_assistant_mode,
    format_product_search_options
)
from utils.user_handlers import handle_new_user_flow
from utils.product_handlers import handle_product_search_options, handle_specific_product_info
from utils.assistant_handlers import handle_assistant_mode

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Variables globales para seguimiento de estado
last_interaction_time = {}
timers = {}
user_state = {}

def inactivity_warning(user_number):
    """
    Maneja el tiempo de inactividad del usuario y envía una despedida.
    
    Args:
        user_number (str): Número de teléfono del usuario
    """
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

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    # Obtener detalles del mensaje entrante
    incoming_message = request.values.get('Body', '').strip()
    user_number = request.values.get('From').replace('whatsapp:', '')

    # Inicializar respuesta
    response = MessagingResponse()
    last_interaction_time[user_number] = time.time()

    # Gestionar temporizador de inactividad
    if user_number in timers:
        timers[user_number].cancel()
    timers[user_number] = Timer(300, inactivity_warning, args=[user_number])
    timers[user_number].start()

    # Verificar si el usuario existe
    user = user_exists(user_number)

    # Flujo para usuarios no registrados
    if not user:
        return handle_new_user_flow(user_number, incoming_message, response, user_state)

    # Flujo para búsqueda de productos
    if user_state.get(user_number) == 'product_search_options':
        return handle_product_search_options(user_number, incoming_message, response, user, user_state)

    # Flujo para información de producto específico
    if user_state.get(user_number) == 'product_info':
        return handle_specific_product_info(user_number, incoming_message, response, user_state)

    # Flujo para modo asistente
    if user_state.get(user_number) == 'assistant_mode':
        return handle_assistant_mode(user_number, incoming_message, response)

    # Flujo principal para usuarios registrados
    return _handle_main_menu_flow(user_number, incoming_message, response, user)

def _handle_main_menu_flow(user_number, incoming_message, response, user):
    """Maneja las opciones del menú principal para usuarios registrados."""
    name, company = user
    
    if incoming_message.lower() == "hola" or incoming_message not in ['1', '2', '3', '4', '5', '6']:
        response.message(create_menu_message(name, company))
    else:
        # Manejo de opciones del menú principal
        if incoming_message == '1':
            response.message(format_about_us())
        elif incoming_message == '2':
            response.message(format_contact_info())
        elif incoming_message == '3':
            user_state[user_number] = 'assistant_mode'
            response.message(format_assistant_mode())
        elif incoming_message == '4':
            responses = get_user_responses(user_number)
            formatted_history = format_history(responses)
            # Enviar todo el historial en un solo mensaje
            response.message(formatted_history)
        elif incoming_message == '6':
            response.message(format_goodbye(name))
            del last_interaction_time[user_number]
            timers[user_number].cancel()
            del timers[user_number]
            user_state.pop(user_number, None)
        elif incoming_message == '5':
            response.message(format_product_search_options())
            user_state[user_number] = 'product_search_options'

    save_message(user_number, incoming_message, 'User')
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)