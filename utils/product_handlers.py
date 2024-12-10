from .product_fetcher import get_product_info #
from .message_formatter import format_product_info #
from .db_helpers import save_message #

def handle_product_search_options(user_number, incoming_message, response, user, user_state):
    name, company = user
    if incoming_message == '1':
        user_state[user_number] = 'product_info'
        """ Opción 1: Cambia el estado a 'product_info' y redirige a la lógica en utils.product_handlers.py -> handle_specific_product_info. """
        response.message(
            "Por favor, ingresa el nombre exacto del producto que estás buscando"
        )
    elif incoming_message == '2':
        user_state[user_number] = 'assistant_mode'
        """ Opción 2: Cambia el estado a 'assistant_mode' y redirige a la lógica en openai.chat_mode.py -> handle_assistant_mode. """
        response.message(
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

""" Es utilizado en -> utils/product_handlers.py opción 1"""
def handle_specific_product_info(user_number, incoming_message, response, user_state):
    product_info = get_product_info(incoming_message)
    save_message(user_number, product_info, 'Bot')
    response.message(format_product_info(product_info))
    user_state[user_number] = 'menu_shown'
    return str(response)
