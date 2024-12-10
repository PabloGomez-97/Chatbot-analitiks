import os
from datetime import datetime
from twilio.rest import Client
from utils.global_state import user_state, timers, last_interaction_time #

                """ Utilizado en -> utils.user_handlers.py """
def format_consent_request():
    return (
        "🔒 *Consentimiento requerido*\n"
        "Antes de continuar, necesitamos tu consentimiento para procesar tus datos de acuerdo con nuestra política de privacidad.\n"
        "https://business.whatsapp.com/policy\n"
        "Por favor, responde *'si'* para aceptar y continuar, o cualquier otra cosa para finalizar la conversación."
    )


def format_timestamp(timestamp):
    return timestamp.strftime("%d/%m/%Y %H:%M")

                """ Utilizado en -> utils/user_handlers.py """
                """ Utilizado en -> controllers/openai/chat_mode.py """
def create_menu_message(name, company):
    return (
        f"👋 ¡Hola {name} de *{company}*!\n\n"
        "¿Cómo podemos ayudarte hoy? 🤝\n\n"
        "📌 *MENÚ PRINCIPAL*\n"
        "━━━━━━━━━━━━━━━\n"
        "1️⃣ *¿Quiénes somos?* 🏢\n"
        "2️⃣ *Contacto* 📱\n"
        "3️⃣ *Asistente técnico (IA)* 🤖\n"
        "4️⃣ *Ver historial completo* 📝\n"
        "5️⃣ *Información de productos* 📦\n"
        "6️⃣ *Finalizar conversación* 👋\n"
        "7️⃣ *Hablar con un ejecutivo de ventas* 💼\n\n"
        "_Selecciona un número para continuar_"
    )

                """ Utilizado en -> utils/product_handlers.py """
def format_product_info(product_info):
    #Formatea la información del producto de manera atractiva
    return (
        f"{product_info}\n\n"
        "_Para más detalles, contacta a nuestro equipo comercial, escribe 'salir' para volver al menú principal_"
    )


def format_history(responses, name):
    if not responses:
        return "<p>No hay mensajes registrados del cliente.</p>"

    formatted_history = "<div style='background-color: #f9f9f9; padding: 10px; border-radius: 8px;'>"
    formatted_history += "<h3 style='color: #4CAF50;'>Historial de Conversación</h3>"

    for response in responses:
        message = response[0]
        timestamp = response[2]
        formatted_history += f"""
        <div style='margin-bottom: 10px; padding: 10px; background: #e8f5e9; border-radius: 5px;'>
            <p><strong>{name}:</strong> {message}</p>
            <small style='color: #666;'>{timestamp.strftime('%d/%m/%Y %H:%M')}</small>
        </div>
        """

    formatted_history += "</div>"
    return formatted_history

def handle_option_7(user_number, response):
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        conversation_sid = os.getenv('TWILIO_CONVERSATION_SID')
        client = Client(account_sid, auth_token)
        participants = client.conversations \
                             .v1 \
                             .conversations(conversation_sid) \
                             .participants \
                             .list()

        if not any(p.identity == user_number for p in participants):
            client.conversations \
                  .v1 \
                  .conversations(conversation_sid) \
                  .participants \
                  .create(identity=user_number)

        user_state[user_number] = 'executive_mode'
        client.conversations \
              .v1 \
              .conversations(conversation_sid) \
              .messages \
              .create(author="system", body="Te hemos conectado con un representante humano. Por favor, espera mientras te respondemos.")
        response.message(
            "👨‍💼 Ahora estás conectado con un humano. Si deseas salir de la conversación, escribe 'salir'."
        )
        return str(response)

    except Exception as e:
        print(f"Error en la opción 7: {str(e)}")
        response.message(
            "⚠️ Lo sentimos, ocurrió un problema al conectarte con un representante. Por favor, intenta de nuevo más tarde."
        )
        return str(response)

                    """ Utilizado en -> utils.user_handlers.py """
def format_welcome_message():
    return (
        "👋 *¡Bienvenido a Analitiks!*\n\n"
        "Para brindarte una mejor atención, necesitamos algunos datos:\n\n"
        "🎯 Por favor, ingresa tu *nombre completo*"
    )
                    """ Utilizado en -> utils.user_handlers.py """
def format_company_request():
    return (
        "¡Gracias! ✨\n\n"
        "🏢 Ahora, por favor ingresa el *nombre de tu empresa*"
    )

def handle_product_search(user_number, incoming_message, response, user_state, name, company):
    if incoming_message.lower() == "salir":
        user_state.pop(user_number, None)
        response.message(f"Has salido del modo de búsqueda de productos, {name}. Volviendo al menú principal...")
        response.message(create_menu_message(name, company))
        return str(response)

    response.message(format_product_search_options())
    return str(response)

def format_product_search_options():
    return (
        "Por favor selecciona una opción:\n\n"
        "1️⃣ *Conozco el nombre del producto*\n"
        "2️⃣ *No conozco el nombre del producto*\n\n"
        "_Nuestro asistente virtual te ayudará a encontrar lo que necesitas, escribe 'salir' para volver al menú principal_"
    )


def format_about_us():
    return (
        "Somos la única compañía nacional 100% dedicada a entregar la más alta tecnología "
        "de análisis en línea para procesos industriales en Chile. 🇨🇱\n\n"
        "_¡Estamos aquí para ayudarte a optimizar tus procesos!_"
    )

def format_contact_info():
    return (
        "📧 Email: info@analitiks.cl\n"
        "📞 Teléfono: +56 9 9918 5050 o +56 9 9799 8501\n"
        "🌐 Web: www.analitiks.cl\n\n"
        "_¡Esperamos tu mensaje!_"
    )

def format_goodbye(name):
    return (
        f"Gracias por contactar con Analitiks, {name}.\n"
        "¡Que tengas un excelente día! ✨"
    )

def format_assistant_mode():
    return (
        "¿En qué puedo ayudarte hoy? Describe tu consulta técnica y "
        "te brindaré la mejor asistencia posible. Escribe 'salir' para volver al menú principal."
    )

                """ Utilizado en -> controllers/openai/openai.py """
def format_assistant_response(response):
    return (
        f"{response}\n\n"
        "_¿Hay algo más en lo que pueda ayudarte? Escribe 'salir' para volver al menú principal_"
    )