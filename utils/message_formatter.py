from datetime import datetime


def format_timestamp(timestamp):
    return timestamp.strftime("%d/%m/%Y %H:%M")

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
        "6️⃣ *Finalizar conversación* 👋\n\n"
        "_Selecciona un número para continuar_"
    )

def format_product_info(product_info):
    #Formatea la información del producto de manera atractiva
    return (
        f"{product_info}\n\n"
        "_Para más detalles, contacta a nuestro equipo comercial, escribe 'salir' para volver al menú principal_"
    )


def format_history(responses, name):
    # Formatea el historial de conversación asegurando que no se trunque ningún mensaje.
    if not responses:
        return "<p>No hay mensajes registrados del cliente.</p>"

    formatted_history = "<div style='background-color: #f9f9f9; padding: 10px; border-radius: 8px;'>"
    formatted_history += "<h3 style='color: #4CAF50;'>Historial de Conversación</h3>"

    for response in responses:
        message = response[0]  # Mensaje completo
        timestamp = response[2]  # Fecha y hora

        # Formatear el mensaje para HTML
        formatted_history += f"""
        <div style='margin-bottom: 10px; padding: 10px; background: #e8f5e9; border-radius: 5px;'>
            <p><strong>{name}:</strong> {message}</p>
            <small style='color: #666;'>{timestamp.strftime('%d/%m/%Y %H:%M')}</small>
        </div>
        """

    formatted_history += "</div>"
    return formatted_history





def format_welcome_message():
    return (
        "👋 *¡Bienvenido a Analitiks!*\n\n"
        "Para brindarte una mejor atención, necesitamos algunos datos:\n\n"
        "🎯 Por favor, ingresa tu *nombre completo*"
    )

def format_company_request():
    return (
        "¡Gracias! ✨\n\n"
        "🏢 Ahora, por favor ingresa el *nombre de tu empresa*"
    )

def handle_product_search(user_number, incoming_message, response, user_state, name, company):
    #Maneja la búsqueda de productos.
    from .message_formatter import create_menu_message

    # Verificar si el usuario quiere salir al menú principal
    if incoming_message.lower() == "salir":
        # Limpiar el estado del usuario
        user_state.pop(user_number, None)
        
        # Mensaje de salida y regreso al menú principal
        response.message(f"Has salido del modo de búsqueda de productos, {name}. Volviendo al menú principal...")
        response.message(create_menu_message(name, company))  # Generar el menú principal con el nombre
        return str(response)

    # Mostrar opciones de búsqueda de productos
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

def format_assistant_response(response):
    return (
        f"{response}\n\n"
        "_¿Hay algo más en lo que pueda ayudarte? Escribe 'salir' para volver al menú principal_"
    )

# Revisado el día 30 de noviembre del 2024