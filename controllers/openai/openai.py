import openai
from datetime import datetime, timedelta
from controllers.smtp.smtp_utils import notify_executive_smtp
from controllers.smtp.smtp_executive import notify_executive_smtp1
from utils.db_helpers import user_exists
from controllers.openai.keywords import keywords_quote, keywords_human, keywords_product


chat_sessions = {}

""" Es utilizado en -> controllers/openai/chat_mode.py """
def ask_openai(client_id, question, name, company, user_number, user_state, response):

    # Verificar si el cliente tiene una sesión activa
    if client_id not in chat_sessions or chat_sessions[client_id]['last_interaction'] < datetime.now() - timedelta(minutes=5):
        chat_sessions[client_id] = {'history': [], 'last_interaction': datetime.now()}
    
    chat_sessions[client_id]['last_interaction'] = datetime.now()
    
    # Preparar historial para OpenAI
    history = chat_sessions[client_id]['history']
    messages = [{"role": "system", "content": "Eres un asistente de ventas que ayuda a resolver dudas de dispositivos de medición enfocado en la empresa Analitiks."}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    """ Si el usuario pregunta por una cotización, notificar a un ejecutivo """
    if any(keyword in question.lower() for keyword in keywords_quote):
        name, company = user_exists(client_id)
        notify_executive_smtp(client_id, name, company, question)
        return (
            "Le hemos notificado a uno de nuestros asesores para que se ponga en contacto con usted a la brevedad.\n\n"
            "En el caso que necesite atención inmediata, favor contactar a nuestros canales directos:\n"
            "👤 *Ejecutivo Alfredo Matus*\n"
            "   📞 Teléfono: +56 9 9799 8501\n"
            "   📧 Correo: alfredo.matus@analitiks.cl\n\n"
            "👤 *Ejecutivo Sebastián Alfaro*\n"
            "   📞 Teléfono: +56 9 9918 5050\n"
            "   📧 Correo: sebastian.alfaro@analitiks.cl\n\n"
        )

    """ Si el usuario pregunta por un ejecutivo, notificar a un ejecutivo """
    if any(keyword in question.lower() for keyword in keywords_human):
        notify_executive_smtp1(client_id, name, company, question)
        user_state[user_number] = 'executive_mode'
        return (
            "¡Espéranos en línea mientras buscamos un agente! 🙌"
        )
    
    """ Si el usuario pregunta por productos, enviarlo a la página https://analitiks.cl/categoria-producto/productos/ """
    if any(keyword in question.lower() for keyword in keywords_product):
        user_state[user_number] = 'product_info'
        return (
            "Te invitamos a revisar nuestra página web https://analitiks.cl/categoria-producto/productos/ para conocer más sobre nuestros productos.\n\n"
            "Si tienes una duda respecto a un producto en especifico, por favor escriba el nombre del producto y te entregaremos más información.\n\n"
            "Para salir al menú principal, solo escriba _'salir'_."
        )
    
    
    try:
        # Procesar mensaje con OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        answer = response['choices'][0]['message']['content'].strip()

        # Actualizar historial del chat
        chat_sessions[client_id]['history'].append({"role": "user", "content": question})
        chat_sessions[client_id]['history'].append({"role": "assistant", "content": answer})
        
        return answer
    
    except Exception as e:
        return (
            "Hubo un error al procesar tu solicitud. Por favor, contacta al número +56 9 9918 5050 o +56 9 9799 8501 "
            "o al correo info@analitiks.cl para asistencia."
        )
