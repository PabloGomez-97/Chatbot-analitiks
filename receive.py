import os
import time
from threading import Timer
import openai 
from flask import Flask, request, jsonify 
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from utils.global_state import user_state, timers, last_interaction_time

from routes.products import products_bp
from routes.leads import leads_bp
from routes.users import users_bp
from routes.messages import messages_bp

from utils.db_helpers import (
    get_db_connection,
    save_message,
    get_user_responses,
    user_exists
)

from controllers.twilio.connect_to_executives import handle_option_7

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
from utils.product_handlers import (
    handle_product_search_options,
    handle_specific_product_info,
    fetch_and_save_products_json)

from controllers.openai.chat_mode import handle_assistant_mode

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


app.register_blueprint(products_bp)
app.register_blueprint(leads_bp)
app.register_blueprint(users_bp)
app.register_blueprint(messages_bp)


def _handle_main_menu_flow(user_number, incoming_message, response, user):
    name, company = user  # Extraer `name` y `company` del usuario

    # Verificar si el usuario está en un estado específico
    current_state = user_state.get(user_number)
    if current_state == 'product_search_options':
        return handle_product_search_options(user_number, incoming_message, response, user, user_state)
    
    current_state = user_state.get(user_number)
    if current_state == 'product_info':
        return handle_specific_product_info(user_number, incoming_message, response, user_state, name, company)

    # Flujo principal para el menú inicial
    if incoming_message.lower() == "hola" or incoming_message not in ['1', '2', '3', '4', '5', '6']:
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
            response.message(format_product_search_options())
            user_state[user_number] = 'product_search_options'
        elif incoming_message == '6':
            response.message(format_goodbye(name))
            del last_interaction_time[user_number]
            timers[user_number].cancel()
            del timers[user_number]
            user_state.pop(user_number, None)
        elif incoming_message == '5':
            return handle_option_7(user_number, response)

    save_message(user_number, incoming_message, 'User')
    return str(response)


def inactivity_warning(user_number):
    if user_number in last_interaction_time:
        current_time = time.time()
        if current_time - last_interaction_time[user_number] > 300:
            print(f"Despedida enviada a {user_number}")
            last_interaction_time.pop(user_number, None)
            if user_number in timers:
                timers[user_number].cancel()
                timers.pop(user_number, None)


@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_message = request.values.get('Body', '').strip().lower()
    user_number = request.values.get('From').replace('whatsapp:', '')

    response = MessagingResponse()
    last_interaction_time[user_number] = time.time()

    if user_number in timers:
        timers[user_number].cancel()
    timers[user_number] = Timer(300, inactivity_warning, args=[user_number])
    timers[user_number].start()

    # Verificar si el usuario existe
    user = user_exists(user_number)

    # Si el usuario no está registrado
    if not user:
        return handle_new_user_flow(user_number, incoming_message, response, user_state)

    # Extraer `name` y `company` del usuario registrado
    name, company = user

    if user_state.get(user_number) == 'executive_mode':
        if incoming_message == "salir":
            user_state.pop(user_number, None)
            response.message(create_menu_message(name, company))
        else:
            response.message()
        return str(response)

    if user_state.get(user_number) == 'assistant_mode':
        return handle_assistant_mode(user_number, incoming_message, response, user_state, name, company)

    # Manejar otros flujos
    return _handle_main_menu_flow(user_number, incoming_message, response, user)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)