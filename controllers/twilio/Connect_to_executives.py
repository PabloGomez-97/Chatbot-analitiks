from twilio.rest import Client
import os
import threading
import time
from utils.global_state import user_state, timers, last_interaction_time

""" Utilizado en -> receive.py """
def handle_option_7(user_number, response):
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        conversation_sid = os.getenv('TWILIO_CONVERSATION_SID')
        client = Client(account_sid, auth_token)
        participants = client.conversations \
                             .v1 \
                             .conversations(conversation_sid) \
                             .participants \
                             .list()

        if not any(p.identity == user_number for p in participants):
            client.conversations \
                  .v1 \
                  .conversations(conversation_sid) \
                  .participants \
                  .create(identity=user_number)

        user_state[user_number] = 'executive_mode'
        client.conversations \
              .v1 \
              .conversations(conversation_sid) \
              .messages \
              .create(author="system", body="¡Espéranos en línea mientras buscamos un agente! 🙌")
        time.sleep(10)
        response.message(
            "👨‍💼 Has sido conectado con un ejecutivo de ventas, cuéntame en qué puedo ayudarte. \n\n Si deseas salir de la conversación, escribe 'salir'."
        )
        return str(response)

    except Exception as e:
        print(f"Error en la opción 7: {str(e)}")
        response.message(
            "⚠️ Lo sentimos, ocurrió un problema al conectarte con un representante. Por favor, intenta de nuevo más tarde."
        )
        return str(response)
