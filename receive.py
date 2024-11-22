import os
import time
from threading import Timer

import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Importaciones personalizadas
from utils.product_fetcher import (
    fetch_and_save_products_json, 
    get_product_info
)
from utils.db_helpers import (
    get_db_connection, 
    save_message, 
    get_user_responses, 
    user_exists, 
    save_user
)
from utils.openai import ask_openai
from utils.message_formatter import (
    format_timestamp,
    create_menu_message,
    format_product_info,
    format_history,
    format_welcome_message,
    format_company_request,
    format_product_search_options,
    format_about_us,
    format_contact_info,
    format_goodbye,
    format_assistant_mode,
    format_assistant_response
)

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
    cursor = conn.cursor(dictionary=True)  # dictionary=True para retornar un formato JSON directo
    cursor.execute("SELECT * FROM users WHERE `create` >= NOW() - INTERVAL 1 DAY")
    users = cursor.fetchall()
    conn.close()
    return {"users": users}, 200


#crear un endpoint para revisar los users actuales que estan en la base de datos
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
        return _handle_new_user_flow(user_number, incoming_message, response)

    # Flujo para búsqueda de productos
    if user_state.get(user_number) == 'product_search_options':
        return _handle_product_search_options(user_number, incoming_message, response, user)

    # Flujo para información de producto específico
    if user_state.get(user_number) == 'product_info':
        return _handle_specific_product_info(user_number, incoming_message, response)

    # Flujo para modo asistente
    if user_state.get(user_number) == 'assistant_mode':
        return _handle_assistant_mode(user_number, incoming_message, response)

    # Flujo principal para usuarios registrados
    return _handle_main_menu_flow(user_number, incoming_message, response, user)

def _handle_new_user_flow(user_number, incoming_message, response):
    """Maneja el flujo de registro de nuevos usuarios."""
    if user_number not in user_state:
        user_state[user_number] = 'awaiting_name'
        response.message(format_welcome_message())
    elif user_state[user_number] == 'awaiting_name':
        user_state[user_number] = 'awaiting_company'
        user_state['name'] = incoming_message
        response.message(format_company_request())
    elif user_state[user_number] == 'awaiting_company':
        name = user_state.pop('name')
        save_user(user_number, name, incoming_message)
        user_state[user_number] = 'registered'
        response.message(create_menu_message(name, incoming_message))
    return str(response)

def _handle_product_search_options(user_number, incoming_message, response, user):
    """Maneja las opciones de búsqueda de productos."""
    name, company = user
    
    if incoming_message == '1':
        user_state[user_number] = 'product_info'
        response.message(
            "🔍 *BÚSQUEDA DE PRODUCTO*\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Por favor, ingresa el nombre exacto del producto que estás buscando"
        )
    elif incoming_message == '2':
        user_state[user_number] = 'assistant_mode'
        response.message(
            "🤖 *ASISTENTE DE BÚSQUEDA*\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Describe el producto que necesitas y te ayudaré a encontrarlo"
        )
    else:
        response.message(
            "⚠️ *Opción no válida*\n\n"
            "Por favor selecciona:\n"
            "1️⃣ *Conozco el nombre del producto*\n"
            "2️⃣ *No conozco el nombre del producto*"
        )
    return str(response)

def _handle_specific_product_info(user_number, incoming_message, response):
    """Maneja la búsqueda de información de un producto específico."""
    product_info = get_product_info(incoming_message)
    save_message(user_number, product_info, 'Bot')
    response.message(format_product_info(product_info))
    user_state[user_number] = 'menu_shown'
    return str(response)

def _handle_assistant_mode(user_number, incoming_message, response):
    """Maneja el modo de asistente de IA."""
    respuesta_ai = ask_openai(incoming_message)
    save_message(user_number, respuesta_ai, 'Bot')
    response.message(format_assistant_response(respuesta_ai))
    return str(response)

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