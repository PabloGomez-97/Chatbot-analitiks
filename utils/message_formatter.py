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
        "5️⃣ *Finalizar conversación* 👋\n"
        "6️⃣ *Información de productos* 📦\n\n"
        "_Selecciona un número para continuar_"
    )

def format_product_info(product_info):
    #Formatea la información del producto de manera atractiva
    return (
        "📦 *INFORMACIÓN DEL PRODUCTO*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{product_info}\n\n"
        "_Para más detalles, contacta a nuestro equipo comercial_"
    )

def format_history(responses):
    #Formatea el historial de conversación asegurando que no exceda los límites de WhatsApp.
    if not responses:
        return "📝 *HISTORIAL*\n━━━━━━━━\n\n_No hay conversaciones registradas_"
    
    try:
        # Encabezado
        formatted_history = "📝 *HISTORIAL DE CONVERSACIÓN*\n━━━━━━━━━━━━━━━━━━\n\n"
        
        # Procesar cada mensaje
        for message, sender, timestamp in responses:
            # Convertir el mensaje a string y limpiar
            message = str(message).strip()
            if len(message) > 200:  # Limitar longitud individual de mensajes
                message = message[:197] + "..."
            
            # Agregar el mensaje al historial
            icon = "Tú" if sender == "User" else "🤖"
            formatted_time = format_timestamp(timestamp)
            formatted_history += f"{icon} [{formatted_time}]\n{message}\n\n"
            
        # Si el mensaje es muy largo, tomar solo los últimos mensajes
        if len(formatted_history) > 1500:  # WhatsApp tiene un límite aproximado de 1600 caracteres
            formatted_history = (
                "📝 *HISTORIAL DE CONVERSACIÓN* (últimos mensajes)\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                + formatted_history[-1400:]  # Dejar espacio para el encabezado
            )
        
        return formatted_history
        
    except Exception as e:
        print(f"Error formateando historial: {str(e)}")
        return "❌ Lo siento, hubo un error al recuperar el historial."

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

def format_product_search_options():
    return (
        "📦 *INFORMACIÓN DE PRODUCTOS*\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "Por favor selecciona una opción:\n\n"
        "1️⃣ *Conozco el nombre del producto*\n"
        "2️⃣ *No conozco el nombre del producto*\n\n"
        "_Nuestro asistente virtual te ayudará a encontrar lo que necesitas_"
    )

def format_about_us():
    return (
        "🏢 *SOBRE ANALITIKS*\n"
        "━━━━━━━━━━━━━━\n\n"
        "Somos la única compañía nacional 100% dedicada a entregar la más alta tecnología "
        "de análisis en línea para procesos industriales en Chile. 🇨🇱\n\n"
        "_¡Estamos aquí para ayudarte a optimizar tus procesos!_"
    )

def format_contact_info():
    return (
        "📱 *INFORMACIÓN DE CONTACTO*\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "📧 Email: contacto@analitiks.cl\n"
        "🌐 Web: www.analitiks.cl\n\n"
        "_¡Esperamos tu mensaje!_"
    )

def format_goodbye(name):
    return (
        "👋 *¡HASTA PRONTO!*\n"
        "━━━━━━━━━━━━━\n\n"
        f"Gracias por contactar con Analitiks, {name}.\n"
        "¡Que tengas un excelente día! ✨"
    )

def format_assistant_mode():
    return (
        "🤖 *ASISTENTE TÉCNICO*\n"
        "━━━━━━━━━━━━━━━\n\n"
        "¿En qué puedo ayudarte hoy? Describe tu consulta técnica y "
        "te brindaré la mejor asistencia posible."
    )

def format_assistant_response(response):
    return (
        "🤖 *RESPUESTA DEL ASISTENTE*\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"{response}\n\n"
        "_¿Hay algo más en lo que pueda ayudarte?_"
    )