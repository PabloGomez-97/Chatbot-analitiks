import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import time
from threading import Timer
import mysql.connector
import json
import requests
from bs4 import BeautifulSoup
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
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

last_interaction_time = {}
timers = {}
user_state = {}

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

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_message = request.values.get('Body', '').strip()
    user_number = request.values.get('From').replace('whatsapp:', '')

    response = MessagingResponse()
    last_interaction_time[user_number] = time.time()

    if user_number in timers:
        timers[user_number].cancel()
    timers[user_number] = Timer(300, inactivity_warning, args=[user_number])
    timers[user_number].start()

    user = user_exists(user_number)

    # Flujo para usuarios no registrados
    if not user:
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

    # Flujo para búsqueda de productos
    if user_state.get(user_number) == 'product_search_options':
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

    # Flujo para información de producto específico
    if user_state.get(user_number) == 'product_info':
        product_info = get_product_info(incoming_message)
        save_message(user_number, product_info, 'Bot')
        response.message(format_product_info(product_info))
        user_state[user_number] = 'menu_shown'
        return str(response)

    # Flujo para modo asistente
    if user_state.get(user_number) == 'assistant_mode':
        respuesta_ai = ask_openai(incoming_message)
        save_message(user_number, respuesta_ai, 'Bot')
        response.message(format_assistant_response(respuesta_ai))
        return str(response)

    # Flujo principal para usuarios registrados
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
            response.message(format_history(responses))
        elif incoming_message == '5':
            response.message(format_goodbye(name))
            del last_interaction_time[user_number]
            timers[user_number].cancel()
            del timers[user_number]
            user_state.pop(user_number, None)
        elif incoming_message == '6':
            response.message(format_product_search_options())
            user_state[user_number] = 'product_search_options'

    save_message(user_number, incoming_message, 'User')
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)