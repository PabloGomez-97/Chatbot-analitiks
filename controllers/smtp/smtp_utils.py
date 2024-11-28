import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Configuración de SMTP
SMTP_SERVER = "smtp.mailgun.org"
SMTP_PORT = 587  # Puerto para STARTTLS
SMTP_USER = os.getenv("MAILGUN_SMTP_USER")  # Usuario SMTP (postmaster@tu-dominio)
SMTP_PASSWORD = os.getenv("MAILGUN_SMTP_PASSWORD")  # Contraseña SMTP


def send_email_with_smtp(to_email, subject, client_id, client_name, client_message):
    """
    Función para enviar un correo electrónico utilizando SMTP con un diseño HTML.
    """
    try:
        # Construir la ruta absoluta al archivo HTML
        html_path = os.path.join(os.getcwd(), "html", "email_template.html")

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
