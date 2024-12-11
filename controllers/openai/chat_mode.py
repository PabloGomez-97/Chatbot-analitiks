from controllers.openai.openai import ask_openai #
from utils.message_formatter import format_assistant_response, create_menu_message #
from utils.db_helpers import save_message #

def handle_assistant_mode(user_number, incoming_message, response, user_state, name, company):
    if incoming_message.lower() == "salir":
        user_state.pop(user_number, None)
        response.message(create_menu_message(name, company))
        return str(response)

    respuesta_ai = ask_openai(user_number, incoming_message, name, company)
    save_message(user_number, respuesta_ai, 'Bot')
    response.message(format_assistant_response(respuesta_ai))
    return str(response)