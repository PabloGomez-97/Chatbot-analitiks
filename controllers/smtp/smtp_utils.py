import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import requests  # Para llamar al endpoint y obtener el historial

# Cargar variables del archivo .env
load_dotenv()

# Configuración de SMTP
SMTP_SERVER = "smtp.mailgun.org"
SMTP_PORT = 587  # Puerto para STARTTLS
SMTP_USER = os.getenv("MAILGUN_SMTP_USER")  # Usuario SMTP (postmaster@tu-dominio)
SMTP_PASSWORD = os.getenv("MAILGUN_SMTP_PASSWORD")  # Contraseña SMTP

# URL del endpoint que devuelve el historial de conversaciones
HISTORY_ENDPOINT = "http://34.224.89.101:9090/getmessages"

def format_client_history(responses):
    """
    Formatea el historial de conversaciones en HTML con estilo de chat.
    """
    if not responses:
        return "<p>No hay mensajes registrados del cliente.</p>"

    formatted_history = ""
    for response in responses:
        # Manejo seguro de cada campo
        message = response[0]  # Primer campo: mensaje
        timestamp = response[2] if len(response) > 2 else None  # Tercer campo opcional: timestamp

        formatted_history += f"""
        <div class="message user">
            <p>{message}</p>
            <div class="timestamp">{timestamp.strftime('%d/%m/%Y %H:%M') if timestamp else ''}</div>
        </div>
        """
    return formatted_history




def send_email_with_smtp(to_email, subject, client_id, client_name, client_message, client_history, client_company):
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
                         .replace("{{client_history}}", client_history)
                         .replace("{{client_company}}", client_company)  # Añadir compañía del cliente
        )


        # Crear el mensaje con el contenido HTML
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



def notify_executive_smtp(client_id, client_name, client_company, question):
    """
    Notifica al ejecutivo sobre una solicitud de cotización e incluye el historial del cliente.
    """
    try:
        # Llamar al endpoint para obtener el historial del cliente
        response = requests.get(HISTORY_ENDPOINT, params={"user_number": client_id})

        if response.status_code != 200:
            print(f"Error al recuperar historial: {response.json()}")
            client_history = "No se pudo recuperar el historial de conversaciones."
        else:
            client_history = response.json().get("history", "No hay historial disponible.")

        # Enviar el correo al ejecutivo
        subject = f"Nueva Solicitud de Cotización de {client_name}"
        send_email_with_smtp(
            to_email="pgomezvillouta@gmail.com",
            subject=subject,
            client_id=client_id,
            client_name=client_name,
            client_company=client_company,  # Asegúrate de que este parámetro se incluya
            client_message=question,
            client_history=client_history
        )

    except Exception as e:
        print(f"Error al notificar al ejecutivo: {e}")
