import openai
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Configuración de SMTP
SMTP_SERVER = "smtp.mailgun.org"
SMTP_PORT = 587  # Puerto para STARTTLS
SMTP_USER = os.getenv("MAILGUN_SMTP_USER")  # Usuario SMTP (postmaster@tu-dominio)
SMTP_PASSWORD = os.getenv("MAILGUN_SMTP_PASSWORD")  # Contraseña SMTP

chat_sessions = {}

def send_email_with_smtp(to_email, subject, client_id, client_name, client_message):
    """
    Función para enviar un correo electrónico utilizando SMTP con un diseño HTML.
    """
    try:
        # Construir la ruta absoluta al archivo HTML
        html_path = os.path.join(os.getcwd(), "HTML", "email_template.html")

        # Leer el archivo HTML de plantilla
        with open(html_path, "r", encoding="utf-8") as file:
            html_template = file.read()

        # Reemplazar variables en la plantilla
        html_content = (
            html_template.replace("{{client_id}}", client_id)
                         .replace("{{client_name}}", client_name)
                         .replace("{{client_message}}", client_message)
        )

        # Crear el mensaje
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        # Adjuntar el contenido HTML
        msg.attach(MIMEText(html_content, "html"))

        # Conectar al servidor SMTP y enviar el correo
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Iniciar comunicación segura
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
            print("Correo enviado exitosamente mediante SMTP con HTML.")

    except Exception as e:
        print(f"Error al enviar correo mediante SMTP: {e}")


def notify_executive_smtp(client_id, client_name, question):
    """
    Función para notificar a un ejecutivo sobre una solicitud de cotización.
    """
    subject = "Nueva Solicitud de Cotización"
    send_email_with_smtp("pgomezvillouta@gmail.com", subject, client_id, client_name, question)


def ask_openai(client_id, question, name):
    """
    Función principal para manejar la lógica de OpenAI y enviar correos según las intenciones detectadas.
    """
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
        notify_executive_smtp(client_id, name, question)
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
        
        return answer
    
    except Exception as e:
        return (
            "Hubo un error al procesar tu solicitud. Por favor, contacta al número +56992193809 "
            "o al correo analitiks@contacto.cl para asistencia."
        )

