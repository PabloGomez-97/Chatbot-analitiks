from controllers.openai.openai import ask_openai #
from utils.message_formatter import format_assistant_response, create_menu_message #
from utils.db_helpers import save_message #

""" Es utilizado en -> utils/product_handlers.py opción 2"""
def handle_assistant_mode(user_number, incoming_message, response, user_state, name, company):
    """ Lógica para manejo 'assistant_mode'. Se activa desde handle_product_search_options (en utils.product_handlers.py) cuando el usuario elige la opción 2. """
    if incoming_message.lower() == "salir":
        user_state.pop(user_number, None)
        response.message(f"Has salido del modo asistente, {name}. Volviendo al menú principal...")
        response.message(create_menu_message(name, company))
        return str(response)

    respuesta_ai = ask_openai(user_number, incoming_message, name, company)
    save_message(user_number, respuesta_ai, 'Bot')
    response.message(format_assistant_response(respuesta_ai))
    return str(response)