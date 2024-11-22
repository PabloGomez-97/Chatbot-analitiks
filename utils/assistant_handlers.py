# utils/assistant_handlers.py
def handle_assistant_mode(user_number, incoming_message, response):
    """Maneja el modo de asistente de IA."""
    from .openai import ask_openai
    from .message_formatter import format_assistant_response
    from .db_helpers import save_message
    
    respuesta_ai = ask_openai(incoming_message)
    save_message(user_number, respuesta_ai, 'Bot')
    response.message(format_assistant_response(respuesta_ai))
    return str(response)