import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import requests

load_dotenv()

EXECUTIVE_EMAIL = os.getenv("EXECUTIVE_EMAIL")

SMTP_SERVER = "smtp.mailgun.org"
SMTP_PORT = 587 
SMTP_USER = os.getenv("MAILGUN_SMTP_USER")
SMTP_PASSWORD = os.getenv("MAILGUN_SMTP_PASSWORD")

HISTORY_ENDPOINT = "http://localhost:9090/getmessages"

def format_client_history(responses):
    if not responses:
        return "<p>No hay mensajes registrados del cliente.</p>"

    formatted_history = ""
    for response in responses:
        message = response[0] 
        timestamp = response[2] if len(response) > 2 else None

        formatted_history += f"""
        <div class="message user">
            <p>{message}</p>
            <div class="timestamp">{timestamp.strftime('%d/%m/%Y %H:%M') if timestamp else ''}</div>
        </div>
        """
    return formatted_history

                """ Es utilizado en este mismo código """
def send_email_with_smtp(to_email, subject, client_id, client_name, client_message, client_history, client_company):
    try:
        print(os.getcwd())
        html_path = "/app/html/email_template.html"

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

                """ Es utilizado en openai.openai.py """
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
            to_email=EXECUTIVE_EMAIL, #Atento en agregar el correo en el .env
            subject=subject,
            client_id=client_id,
            client_name=client_name,
            client_company=client_company,
            client_message=question,
            client_history=client_history
        )
    except Exception as e:
        print(f"Error al notificar al ejecutivo: {e}")