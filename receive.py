import os
import time
from threading import Timer
import openai 
from flask import Flask, request, jsonify 
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from utils.globalstate import user_state, timers, last_interaction_time
from routes.products import products_bp
from routes.leads import leads_bp
from routes.users import users_bp
from routes.messages import messages_bp
from utils.dbhelpers import save_message, user_exists
from controllers.twilio.connect2executives import handle_option_5
from utils.messageformatter import create_menu_message, format_about_us, format_contact_info, format_goodbye, format_assistant_mode, format_product_search_options
from twilio.rest import Client
from utils.userconsent import handle_new_user_flow
from utils.producthandlers import handle_specific_product_info
from controllers.openai.openai import handle_assistant_mode

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Routes
app.register_blueprint(products_bp)
app.register_blueprint(leads_bp)
app.register_blueprint(users_bp)
app.register_blueprint(messages_bp)

# Esta función se encarga de manejar el flujo principal de la conversación, o sea, el menú de opciones que el cliente tiene disponible
def _handle_main_menu_flow(user_number, incoming_message, response, user):
    name, company = user

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
            response.message(format_product_search_options(user_number))
        elif incoming_message == '6':
            response.message(format_goodbye(name))
            del last_interaction_time[user_number]
            timers[user_number].cancel()
            del timers[user_number]
            user_state.pop(user_number, None)
        elif incoming_message == '5':
            return handle_option_5(user_number, response)
        
    save_message(user_number, incoming_message, 'User')
    return str(response)


def inactivity_warning(user_number):
    if user_number in last_interaction_time:
        current_time = time.time()
        if current_time - last_interaction_time[user_number] > 180:
            print(f"Warning 1 enviado a {user_number}")
            client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            try:
                client.messages.create(
                    body="¿Sigues en línea?",
                    from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
                    to=f"whatsapp:{user_number}"
                )
            except Exception as e:
                print(f"Error al enviar mensaje de inactividad: {e}")

            if f"{user_number}_warning1" in timers:
                timers[f"{user_number}_warning1"].cancel()
                timers.pop(f"{user_number}_warning1", None)


def inactivity_warning2(user_number):
    if user_number in last_interaction_time:
        current_time = time.time()
        if current_time - last_interaction_time[user_number] > 300:
            print(f"Warning 2 enviado a {user_number}")
            client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            try:
                client.messages.create(
                    body="Gracias por escribirnos, estamos para ayudarte. 😉",
                    from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
                    to=f"whatsapp:{user_number}"
                )
            except Exception as e:
                print(f"Error al enviar mensaje de inactividad: {e}")

            last_interaction_time.pop(user_number, None)
            if f"{user_number}_warning2" in timers:
                timers[f"{user_number}_warning2"].cancel()
                timers.pop(f"{user_number}_warning2", None)


@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_message = request.values.get('Body', '').strip().lower()
    user_number = request.values.get('From').replace('whatsapp:', '')

    response = MessagingResponse()
    last_interaction_time[user_number] = time.time()

    if f"{user_number}_warning1" in timers:
        timers[f"{user_number}_warning1"].cancel()
    timers[f"{user_number}_warning1"] = Timer(180, inactivity_warning, args=[user_number])
    timers[f"{user_number}_warning1"].start()

    if f"{user_number}_warning2" in timers:
        timers[f"{user_number}_warning2"].cancel()
    timers[f"{user_number}_warning2"] = Timer(300, inactivity_warning2, args=[user_number])
    timers[f"{user_number}_warning2"].start()

    user = user_exists(user_number)

    if not user:
        return handle_new_user_flow(user_number, incoming_message, response, user_state)

    name, company = user

    if user_state.get(user_number) == 'executive_mode':
        if incoming_message == "salir":
            user_state.pop(user_number, None)
            response.message(create_menu_message(name, company))
        else:
            response.message()
        return str(response)

    if user_state.get(user_number) == 'assistant_mode':
        save_message(user_number, incoming_message, 'User') # Si quiero que se guarden los mensajes del mismo assistant_mode, solo hay que agregar este código (puede también para otros estados)
        return handle_assistant_mode(user_number, incoming_message, response, user_state, name, company)
    
    if user_state.get(user_number) == 'product_info':
        return handle_specific_product_info(user_number, incoming_message, response, user_state, name, company)
    
    # Si quiero agregar un nuevo estado, solo tengo que agregar un nuevo if aquí y en el diccionario de user_state, actualmente solo tenemos 3 estados: assistant_mode, executive_mode y product_info
    # Se agrega para que el whatsapp_reply sepa que entrarás a un nuevo estado y no se ejecute el flujo principal de la conversación

    return _handle_main_menu_flow(user_number, incoming_message, response, user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)