# utils/user_handlers.py
def handle_new_user_flow(user_number, incoming_message, response, user_state):
    """Maneja el flujo de registro de nuevos usuarios."""
    from .message_formatter import format_welcome_message, format_company_request, create_menu_message
    from .db_helpers import save_user
    
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
