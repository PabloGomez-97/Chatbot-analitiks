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
from dotenv import load_dotenv

load_dotenv()

# Crear una instancia de la aplicación Flask, la función del Flask es crear una aplicación web que pueda recibir y responder mensajes de WhatsApp
app = Flask(__name__)

#Utilizamos ngrok para exponer nuestro servidor local a internet y poder recibir mensajes de WhatsApp en nuestro servidor local por medio de Twilio.

# Configuración de la clave API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Diccionarios para rastrear el estado del usuario y temporizadores de inactividad
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

@app.route('/update_products', methods=['GET']) # Cada vez que se llama al /update_products, se ejecura lo de abajo
def update_products():
    fetch_and_save_products_json()
    return "Datos de productos actualizados y guardados en productos.json", 200

# Endpoint principal para recibir y responder mensajes de WhatsApp
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_message = request.values.get('Body', '').strip()
    user_number = request.values.get('From').replace('whatsapp:', '')

    response = MessagingResponse()
    last_interaction_time[user_number] = time.time()

    # Reiniciar temporizador de inactividad
    if user_number in timers:
        timers[user_number].cancel()
    timers[user_number] = Timer(300, inactivity_warning, args=[user_number])
    timers[user_number].start()

    # Verificar si el usuario ya existe
    user = user_exists(user_number)

    # Flujo de registro
    if not user:
        if user_number not in user_state:
            user_state[user_number] = 'awaiting_name'
            response.message("👋 ¡Bienvenido a Analitiks! Antes de continuar, por favor ingresa tu *nombre*.")
        elif user_state[user_number] == 'awaiting_name':
            user_state[user_number] = 'awaiting_company'
            user_state['name'] = incoming_message
            response.message("Gracias, ahora por favor ingresa el nombre de tu *empresa*.")
        elif user_state[user_number] == 'awaiting_company':
            name = user_state.pop('name')
            save_user(user_number, name, incoming_message)
            user_state[user_number] = 'registered'
            response.message(f"¡Gracias {name}! ¿Cómo puedo ayudarte hoy?\n\n"
                             "1️⃣ *¿Quiénes somos?*\n"
                             "2️⃣ *Contacto*\n"
                             "3️⃣ *Asistente técnico (IA)*\n"
                             "4️⃣ *Ver historial completo*\n"
                             "5️⃣ *Finalizar conversación*\n"
                             "6️⃣ *Información de productos*\n")
        return str(response)

    # Verificar estados específicos antes del menú principal
    if user_state.get(user_number) == 'product_search_options':
        if incoming_message == '1':
            user_state[user_number] = 'product_info'
            response.message("Perfecto, por favor ingresa el nombre exacto del producto que estás buscando.")
        elif incoming_message == '2':
            user_state[user_number] = 'assistant_mode'
            response.message("Entendido, dime qué necesitas y nuestro asistente técnico con IA te ayudará.")
        else:
            response.message("Opción no válida. Por favor selecciona:\n"
                             "1️⃣ *Conozco el nombre del producto*\n"
                             "2️⃣ *No conozco el nombre del producto*")
        return str(response)

    if user_state.get(user_number) == 'product_info':
        product_info = get_product_info(incoming_message)
        save_message(user_number, product_info, 'Bot')
        response.message(product_info)
        user_state[user_number] = 'menu_shown'  # Regresar al menú principal después de la respuesta
        return str(response)

    if user_state.get(user_number) == 'assistant_mode':
        respuesta_ai = ask_openai(incoming_message)
        save_message(user_number, respuesta_ai, 'Bot')
        response.message(respuesta_ai)
        return str(response)

    # Mostrar menú de opciones si el mensaje es "Hola" o no coincide con ninguna opción
    name, company = user
    if incoming_message.lower() == "hola" or incoming_message not in ['1', '2', '3', '4', '5', '6']:
        response.message(f"Hola {name} de {company}, ¿cómo podemos ayudarte hoy?\n\n"
                         "1️⃣ *¿Quiénes somos?*\n"
                         "2️⃣ *Contacto*\n"
                         "3️⃣ *Asistente técnico (IA)*\n"
                         "4️⃣ *Ver historial completo*\n"
                         "5️⃣ *Finalizar conversación*\n"
                         "6️⃣ *Información de productos*\n")
    else:
        # Flujo de opciones para usuario registrado
        if incoming_message == '1':
            response.message("Analitiks es la única compañía nacional 100% dedicada a entregar la más alta tecnología de análisis en línea para procesos industriales en Chile.")
        elif incoming_message == '2':
            response.message("Contáctanos en: contacto@analitiks.cl o en www.analitiks.cl.")
        elif incoming_message == '3':
            user_state[user_number] = 'assistant_mode'
            response.message("¿Cuál es tu duda técnica? Pregunta lo que necesites saber, nuestro asistente técnico con IA te ayudará.")
        elif incoming_message == '4':
            responses = get_user_responses(user_number)
            historial = "\n".join([f"[{timestamp}] {sender}: {message}" for message, sender, timestamp in responses]) or "No tienes historial."
            response.message(historial)
        elif incoming_message == '5':
            response.message("Gracias por conversar con Analitiks. ¡Hasta luego!")
            del last_interaction_time[user_number]
            timers[user_number].cancel()
            del timers[user_number]
            user_state.pop(user_number, None)
        elif incoming_message == '6':
            response.message("Por favor selecciona una opción:\n"
                             "1️⃣ *Conozco el nombre del producto*\n"
                             "2️⃣ *No conozco el nombre del producto* - No te preocupes, nuestro asistente virtual te ayudará a encontrarlo.")
            user_state[user_number] = 'product_search_options'

    save_message(user_number, incoming_message, 'User')
    return str(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)

