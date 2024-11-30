import openai
from datetime import datetime, timedelta
from controllers.smtp.smtp_utils import notify_executive_smtp
from utils.db_helpers import user_exists


chat_sessions = {}

def ask_openai(client_id, question, name, company):
    # Grupos de palabras clave según la intención
    keywords_quote = [
        "presupuesto", "cotización", "precio", "costo", "cuánto cuesta", "valores", "oferta"
    ]
    keywords_human = [
        "contacto", "hablar con alguien", "asistencia", "ayuda real", "soporte humano", 
        "asesor", "consultar con alguien", "asistente real", "llamar", "cómo contactar",
        "quiero hablar", "comunicarme", "teléfono", "representante", "consultor",
        "hablar con un humano", "necesito hablar con un humano", "atención humana", "quiero un humano",
        "persona", "vendedor", "quiero hablar con alguien", "quiero hablar con un vendedor", "técnico", 
        "quiero hablar con un técnico", "quiero hablar con un asesor", "quiero hablar con un consultor"
    ]

    # Verificar si el cliente tiene un historial activo
    if client_id not in chat_sessions or chat_sessions[client_id]['last_interaction'] < datetime.now() - timedelta(minutes=5):
        # Reiniciar sesión si han pasado más de 5 minutos
        chat_sessions[client_id] = {'history': [], 'last_interaction': datetime.now()}
    
    chat_sessions[client_id]['last_interaction'] = datetime.now()
    
    # Preparar el historial para OpenAI
    history = chat_sessions[client_id]['history']
    messages = [{"role": "system", "content": "Eres un asistente de ventas que ayuda a resolver dudas de dispositivos de medición enfocado en la empresa Analitiks."}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})
    
    # Detectar intención según palabras clave
    if any(keyword in question.lower() for keyword in keywords_quote):
        # Obtener el nombre y la compañía del cliente
        name, company = user_exists(client_id)  # Asegúrate de que esta línea devuelve correctamente la compañía
        notify_executive_smtp(client_id, name, company, question)
        return (
            "Le hemos notificado a uno de nuestros asesores para que se ponga en contacto con usted a la brevedad.\n\n"
            "En el caso que necesite atención inmediata, favor contactar a nuestros canales directos:\n"
            "📞 Número de teléfono: +56 9 9918 5050 o +56 9 9799 8501 \n"
            "📧 Correo electrónico: alfredo.matus@analitiks.cl ó sebastian.alfaro@analitiks.cl"
        )
    
    if any(keyword in question.lower() for keyword in keywords_human):
         # Respuesta para hablar con un humano
        return (
            "Le hemos notificado a uno de nuestros asesores para que se ponga en contacto con usted a la brevedad.\n\n"
            "En el caso que necesite atención inmediata, favor contactar a nuestros canales directos:\n"
            "📞 Número de teléfono: +56 9 9918 5050 o +56 9 9799 8501 \n"
            "📧 Correo electrónico: alfredo.matus@analitiks.cl ó sebastian.alfaro@analitiks.cl"
        )
    
    try:
        # Enviar la solicitud a OpenAI para respuestas generales
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        answer = response['choices'][0]['message']['content'].strip()
        
        # Actualizar el historial
        chat_sessions[client_id]['history'].append({"role": "user", "content": question})
        chat_sessions[client_id]['history'].append({"role": "assistant", "content": answer})
        
        return answer
    
    except Exception as e:
        return (
            "Hubo un error al procesar tu solicitud. Por favor, contacta al número +56 9 9918 5050 o +56 9 9799 8501 "
            "o al correo info@analitiks.cl para asistencia."
        )

# Revisado el día 30 de noviembre del 2024