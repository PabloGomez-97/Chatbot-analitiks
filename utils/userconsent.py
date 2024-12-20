from .messageformatter import format_welcome_message, format_company_request, create_menu_message, format_consent_request
from .dbhelpers import save_user

def handle_new_user_flow(user_number, incoming_message, response, user_state):
    if user_number not in user_state:
        user_state[user_number] = 'awaiting_consent'
        response.message(format_consent_request())
    elif user_state[user_number] == 'awaiting_consent':
        # Solicitar consentimiento del usuario
        if incoming_message.lower() == "si":
            user_state[user_number] = 'awaiting_name'
            response.message(format_welcome_message())
        else:
            response.message(
                "❌ No podemos continuar sin tu consentimiento. "
                "Si cambias de opinión, vuelve a escribirnos. ¡Hasta luego!"
            )
            user_state.pop(user_number, None)
    elif user_state[user_number] == 'awaiting_name': # Pedir nombre del cliente y la empresa
        user_state[user_number] = 'awaiting_company'
        user_state['name'] = incoming_message
        response.message(format_company_request())
    elif user_state[user_number] == 'awaiting_company': # Guardar el usuario y continuar
        name = user_state.pop('name')
        save_user(user_number, name, incoming_message)
        user_state[user_number] = 'registered'
        response.message(create_menu_message(name, incoming_message))
    return str(response)
