def handle_assistant_mode(user_number, incoming_message, response, user_state, name, company):
    from controllers.openai.openai import ask_openai
    from utils.message_formatter import format_assistant_response, create_menu_message
    from utils.db_helpers import save_message

    # Verificar si el usuario quiere salir del modo asistente
    if incoming_message.lower() == "salir":
        # Limpiar el estado del usuario
        user_state.pop(user_number, None)
        
        # Mensaje de salida y regreso al menú principal
        response.message(f"Has salido del modo asistente, {name}. Volviendo al menú principal...")
        response.message(create_menu_message(name, company))
        return str(response)

    # Procesar el mensaje con OpenAI
    respuesta_ai = ask_openai(user_number, incoming_message, name, company)
    save_message(user_number, respuesta_ai, 'Bot')
    response.message(format_assistant_response(respuesta_ai))
    return str(response)

# Chequeado el día 30 de noviembre de 2024
