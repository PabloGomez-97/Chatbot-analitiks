import openai
import requests  # Para manejar las solicitudes a la API de Mailgun
from datetime import datetime, timedelta

chat_sessions = {}

# Configuración de Mailgun
MAILGUN_API_KEY = "f874943f195f9449572f002b97b79614-c02fd0ba-655bf0ce"  # Reemplaza con tu clave API de Mailgun
MAILGUN_DOMAIN = "https://app.mailgun.com/app/sending/domains/sandbox8d913135564844ddbf5cf1265f4a3c30.mailgun.org"  # Reemplaza con tu dominio de Mailgun
MAILGUN_FROM_EMAIL = "no-reply@yourdomain.com"  # Correo que aparece como remitente

def send_email_with_mailgun(to_email, subject, body):
    """
    Función para enviar un correo electrónico utilizando Mailgun.
    """
    mailgun_url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    payload = {
        "from": MAILGUN_FROM_EMAIL,
        "to": to_email,
        "subject": subject,
        "text": body
    }
    try:
        response = requests.post(mailgun_url, auth=("api", MAILGUN_API_KEY), data=payload)
        if response.status_code == 200:
            print("Correo enviado exitosamente a través de Mailgun.")
        else:
            print(f"Error al enviar correo: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error al comunicarse con Mailgun: {e}")

def notify_executive_mailgun(client_id, question):
    """
    Función para notificar a un ejecutivo sobre una solicitud de cotización.
    """
    subject = "Nueva Solicitud de Cotización"
    body = (
        f"Se ha recibido una solicitud de cotización de un cliente.\n\n"
        f"ID del cliente: {client_id}\n"
        f"Mensaje del cliente: {question}\n\n"
        f"Por favor, póngase en contacto con el cliente lo antes posible."
    )
    send_email_with_mailgun("contacto@analitiks.cl", subject, body)

def ask_openai(client_id, question):
    # Grupos de palabras clave según la intención
    keywords_quote = [
        "presupuesto", "cotización", "precio", "coste", "cuánto cuesta", "valores"
    ]
    keywords_human = [
        "contacto", "hablar con alguien", "asistencia", "ayuda real", "soporte humano", 
        "asesor", "consultar con alguien", "asistente real", "llamar", "cómo contactar",
        "quiero hablar", "comunicarme", "teléfono", "representante", "consultor",
        "hablar con un humano", "necesito hablar con un humano", "atención humana", "quiero un humano"
    ]

    # Verificar si el cliente tiene un historial activo
    if client_id not in chat_sessions or chat_sessions[client_id]['last_interaction'] < datetime.now() - timedelta(minutes=5):
        # Reiniciar sesión si han pasado más de 5 minutos
        chat_sessions[client_id] = {'history': [], 'last_interaction': datetime.now()}
    
    chat_sessions[client_id]['last_interaction'] = datetime.now()
    
    # Preparar el historial para OpenAI
    history = chat_sessions[client_id]['history']
    messages = [{"role": "system", "content": "Eres un asistente de ventas que ayuda a resolver dudas de dispositivos de medición."}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})
    
    # Detectar intención según palabras clave
    if any(keyword in question.lower() for keyword in keywords_quote):
        notify_executive_mailgun(client_id, question)  # Notificar al ejecutivo con Mailgun
        return (
            "Para nosotros es un placer que quiera realizar un presupuesto con nosotros. Le hemos notificado a uno de nuestros asesores para que se ponga en contacto con usted a la brevedad.\n\n"
            "En el caso que necesite atención inmediata, favor contactar a nuestros canales directos:\n"
            "📞 Número de teléfono: +56 9 9918 5050.\n"
            "📧 Correo electrónico: alfredo.matus@analitiks.cl ó sebastian.alfaro@analitiks.cl"
        )
    
    if any(keyword in question.lower() for keyword in keywords_human):
         # Respuesta para hablar con un humano
        return (
            "Para Analitiks es un placer asistirle. Hemos notificado a nuestros asesores para que se pongan en contacto con usted a la brevedad. Asimismo, le proporcionamos nuestros canales directos para casos en los que se esté comunicando fuera del horario establecido:\n\n"
            "puedes contactar directamente a Analitiks: \n\n"
            "📞 Número de teléfono: +56 9 9918 5050. \n"
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
        
        # Verificar si la respuesta no es útil
        if "no estoy seguro" in answer.lower() or "no sé" in answer.lower():
            return (
                "Lamentablemente, no tengo esa información en este momento. Por favor, contacta a un asistente real "
                "al +56992193809 o escribe a analitiks@contacto.cl para obtener ayuda más detallada."
            )
        
        return answer
    
    except Exception as e:
        return (
            "Hubo un error al procesar tu solicitud. Por favor, contacta al número +56992193809 "
            "o al correo analitiks@contacto.cl para asistencia."
        )
