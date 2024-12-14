import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import requests

load_dotenv()

EXECUTIVE_EMAIL = os.getenv("EXECUTIVE_EMAIL")

SMTP_SERVER = "smtp.mailgun.org"
SMTP_PORT = 587  # Puerto para STARTTLS
SMTP_USER = os.getenv("MAILGUN_SMTP_USER")
SMTP_PASSWORD = os.getenv("MAILGUN_SMTP_PASSWORD")

HISTORY_ENDPOINT = "http://localhost:9090/getmessages"

# SISTEMA DE NOTIFICACIÓN DE COTIZACIÓN POR CORREO ELECTRÓNICO

def send_email_with_smtp(to_email, subject, client_id, client_name, client_message, client_history, client_company):
    try:
        print(os.getcwd())
        html_path = os.path.join(os.getcwd(), "html", "email_template.html") # Principal diferencia entre esta función y la siguiente
        with open(html_path, "r", encoding="utf-8") as file:
            html_template = file.read()
        html_content = (
            html_template.replace("{{client_id}}", client_id)
                         .replace("{{client_name}}", client_name)
                         .replace("{{client_message}}", client_message)
                         .replace("{{client_history}}", client_history)
                         .replace("{{client_company}}", client_company)
        )

        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
            print("Correo enviado exitosamente mediante SMTP con HTML.")

    except Exception as e:
        print(f"Error al enviar correo mediante SMTP: {e}")


def notify_executive_smtp(client_id, client_name, client_company, question):
    try:
        response = requests.get(HISTORY_ENDPOINT, params={"user_number": client_id})

        if response.status_code != 200:
            print(f"Error al recuperar historial: {response.json()}")
            client_history = "No se pudo recuperar el historial de conversaciones."
        else:
            client_history = response.json().get("history", "No hay historial disponible.")

        subject = f"Nueva Solicitud de Cotización de {client_name}"
        send_email_with_smtp(
            to_email=EXECUTIVE_EMAIL,
            subject=subject,
            client_id=client_id,
            client_name=client_name,
            client_company=client_company,
            client_message=question,
            client_history=client_history
        )

    except Exception as e:
        print(f"Error al notificar al ejecutivo: {e}")

# SISTEMA SOLO DE LLAMADAS AL EJECUTIVO DE VENTAS

def send_email_with_smtp1(to_email, subject, client_id, client_name, client_message, client_history, client_company):
    try:
        print(os.getcwd())
        html_path = os.path.join(os.getcwd(), "html", "email_executive.html")
        with open(html_path, "r", encoding="utf-8") as file:
            html_template = file.read()
        html_content = (
            html_template.replace("{{client_id}}", client_id)
                         .replace("{{client_name}}", client_name)
                         .replace("{{client_message}}", client_message)
                         .replace("{{client_history}}", client_history)
                         .replace("{{client_company}}", client_company)
        )

        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
            print("Correo enviado exitosamente mediante SMTP con HTML.")

    except Exception as e:
        print(f"Error al enviar correo mediante SMTP: {e}")


def notify_executive_smtp1(client_id, client_name, client_company, question):
    try:
        response = requests.get(HISTORY_ENDPOINT, params={"user_number": client_id})

        if response.status_code != 200:
            print(f"Error al recuperar historial: {response.json()}")
            client_history = "No se pudo recuperar el historial de conversaciones."
        else:
            client_history = response.json().get("history", "No hay historial disponible.")

        subject = f"Nueva Solicitud de Conversación de {client_name}"
        send_email_with_smtp1(
            to_email=EXECUTIVE_EMAIL,
            subject=subject,
            client_id=client_id,
            client_name=client_name,
            client_company=client_company,
            client_message=question,
            client_history=client_history
        )

    except Exception as e:
        print(f"Error al notificar al ejecutivo: {e}")
