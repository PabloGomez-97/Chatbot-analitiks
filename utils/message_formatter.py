from utils.global_state import user_state


def format_consent_request():
    return (
        "🔒 *Consentimiento requerido*\n"
        "Antes de continuar, necesitamos tu consentimiento para procesar tus datos de acuerdo con nuestra política de privacidad.\n"
        "https://business.whatsapp.com/policy\n"
        "Por favor, responde *'si'* para aceptar y continuar, o cualquier otra cosa para finalizar la conversación."
    )


def format_timestamp(timestamp): # Hay que chequear si se utiliza en algún lado
    return timestamp.strftime("%d/%m/%Y %H:%M")


def create_menu_message(name, company):
    return (
        f"*👋 Hola {name}! Soy tu asistente virtual*\n\n"
        "Escoge una opción para poder ayudarte 👇\n\n"
        "1️⃣ *¿Quiénes somos?* 🏢\n"
        "2️⃣ *Contacto* 📱\n"
        "3️⃣ *Asistente técnico (IA)* 🤖\n"
        "4️⃣ *Información de productos* 📦\n"
        "5️⃣ *Hablar con un ejecutivo de ventas* 💼\n"
        "6️⃣ *Finalizar conversación* 👋"
    )


def format_product_info(product_info):
    return (
        f"{product_info}"
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


def format_welcome_message():
    return (
        "👋 *¡Bienvenido al chat de Analitiks!*\n\n"
        "Para brindarte una mejor atención, necesitamos algunos datos:\n\n"
        "🎯 Por favor, ingresa tu *Nombre*"
    )


def format_company_request():
    return (
        "¡Gracias! ✨\n\n"
        "🏢 Ahora, por favor ingresa el *Nombre de tu Empresa*"
    )


def format_product_search_options(user_number):
    user_state[user_number] = 'product_info'
    return (
        "Te invitamos a revisar nuestra página web https://analitiks.cl/categoria-producto/productos/ para conocer más sobre nuestros productos.\n\n"
        "Si tienes una duda respecto a un producto en especifico, por favor escriba el nombre del producto y te entregaremos más información.\n\n"
        "Para salir al menú principal, solo escriba _'salir'_."
    )


def handle_product_search(user_number, incoming_message, response, user_state, name, company):
    if incoming_message.lower() == "salir":
        user_state.pop(user_number, None)
        response.message(f"Has salido del modo de búsqueda de productos, {name}. Volviendo al menú principal...")
        response.message(create_menu_message(name, company))
        return str(response)

    response.message(format_product_search_options())
    return str(response)


def format_about_us():
    return (
        "Somos la única compañía nacional 100% dedicada a entregar la más alta tecnología "
        "de análisis en línea para procesos industriales en Chile. 🇨🇱\n\n"
        "_¡Estamos aquí para ayudarte a optimizar tus procesos!_"
    )


def format_contact_info():
    return (
        "🌐 Web: www.analitiks.cl\n"
        "📧 Email: info@analitiks.cl\n\n"
        "👤 *Ejecutivo Alfredo Matus*\n"
        "   📞 Teléfono: +56 9 9799 8501\n"
        "   📧 Correo: alfredo.matus@analitiks.cl\n\n"
        "👤 *Ejecutivo Sebastián Alfaro*\n"
        "   📞 Teléfono: +56 9 9918 5050\n"
        "   📧 Correo: sebastian.alfaro@analitiks.cl\n\n"
        "✨ ¡Esperamos tu mensaje!"
    )


def format_goodbye(name):
    return (
        f"Gracias por contactar con Analitiks, {name}.\n"
        "¡Que tengas un excelente día! ✨"
    )


def format_assistant_mode():
    return (
        "¿En qué puedo ayudarte hoy? Describe tu consulta técnica y "
        "te brindaré la mejor asistencia posible.\n\n Escribe 'salir' para volver al menú principal."
    )


def format_assistant_response(response):
    return (
        f"{response}\n\n"
    )