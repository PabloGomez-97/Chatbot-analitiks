"""
Utilidades para el formateo de mensajes de WhatsApp
Este módulo contiene funciones para dar formato visual a los diferentes tipos de mensajes
"""

from datetime import datetime

def format_timestamp(timestamp):
    """
    Formatea la marca de tiempo de manera más legible
    
    Args:
        timestamp: Objeto datetime a formatear
        
    Returns:
        str: Fecha y hora formateada como DD/MM/YYYY HH:MM
    """
    return timestamp.strftime("%d/%m/%Y %H:%M")

def create_menu_message(name, company):
    """
    Crea un mensaje de menú formateado y atractivo
    
    Args:
        name (str): Nombre del usuario
        company (str): Nombre de la empresa
        
    Returns:
        str: Mensaje de menú formateado
    """
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
    """
    Formatea la información del producto de manera atractiva
    
    Args:
        product_info (str): Información del producto
        
    Returns:
        str: Información del producto formateada
    """
    return (
        "📦 *INFORMACIÓN DEL PRODUCTO*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{product_info}\n\n"
        "_Para más detalles, contacta a nuestro equipo comercial_"
    )

def format_history(responses):
    """
    Formatea el historial de manera más legible y atractiva
    
    Args:
        responses (list): Lista de tuplas (mensaje, remitente, timestamp)
        
    Returns:
        str: Historial formateado
    """
    if not responses:
        return "📝 *HISTORIAL*\n━━━━━━━━\n\n_No hay conversaciones registradas_"
    
    formatted_messages = []
    for message, sender, timestamp in responses:
        icon = "👤" if sender == "User" else "🤖"
        formatted_messages.append(f"{icon} [{format_timestamp(timestamp)}]\n{message}\n")
    
    return "📝 *HISTORIAL DE CONVERSACIÓN*\n━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(formatted_messages)

def format_welcome_message():
    """
    Crea un mensaje de bienvenida para nuevos usuarios
    
    Returns:
        str: Mensaje de bienvenida formateado
    """
    return (
        "👋 *¡Bienvenido a Analitiks!*\n\n"
        "Para brindarte una mejor atención, necesitamos algunos datos:\n\n"
        "🎯 Por favor, ingresa tu *nombre completo*"
    )

def format_company_request():
    """
    Crea un mensaje para solicitar el nombre de la empresa
    
    Returns:
        str: Mensaje de solicitud formateado
    """
    return (
        "¡Gracias! ✨\n\n"
        "🏢 Ahora, por favor ingresa el *nombre de tu empresa*"
    )

def format_product_search_options():
    """
    Crea un mensaje con las opciones de búsqueda de productos
    
    Returns:
        str: Mensaje de opciones de búsqueda formateado
    """
    return (
        "📦 *INFORMACIÓN DE PRODUCTOS*\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "Por favor selecciona una opción:\n\n"
        "1️⃣ *Conozco el nombre del producto*\n"
        "2️⃣ *No conozco el nombre del producto*\n\n"
        "_Nuestro asistente virtual te ayudará a encontrar lo que necesitas_"
    )

def format_about_us():
    """
    Crea un mensaje con la información sobre la empresa
    
    Returns:
        str: Mensaje sobre la empresa formateado
    """
    return (
        "🏢 *SOBRE ANALITIKS*\n"
        "━━━━━━━━━━━━━━\n\n"
        "Somos la única compañía nacional 100% dedicada a entregar la más alta tecnología "
        "de análisis en línea para procesos industriales en Chile. 🇨🇱\n\n"
        "_¡Estamos aquí para ayudarte a optimizar tus procesos!_"
    )

def format_contact_info():
    """
    Crea un mensaje con la información de contacto
    
    Returns:
        str: Mensaje de contacto formateado
    """
    return (
        "📱 *INFORMACIÓN DE CONTACTO*\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "📧 Email: contacto@analitiks.cl\n"
        "🌐 Web: www.analitiks.cl\n\n"
        "_¡Esperamos tu mensaje!_"
    )

def format_goodbye(name):
    """
    Crea un mensaje de despedida personalizado
    
    Args:
        name (str): Nombre del usuario
        
    Returns:
        str: Mensaje de despedida formateado
    """
    return (
        "👋 *¡HASTA PRONTO!*\n"
        "━━━━━━━━━━━━━\n\n"
        f"Gracias por contactar con Analitiks, {name}.\n"
        "¡Que tengas un excelente día! ✨"
    )

def format_assistant_mode():
    """
    Crea un mensaje para el modo asistente técnico
    
    Returns:
        str: Mensaje del modo asistente formateado
    """
    return (
        "🤖 *ASISTENTE TÉCNICO*\n"
        "━━━━━━━━━━━━━━━\n\n"
        "¿En qué puedo ayudarte hoy? Describe tu consulta técnica y "
        "te brindaré la mejor asistencia posible."
    )

def format_assistant_response(response):
    """
    Formatea la respuesta del asistente técnico
    
    Args:
        response (str): Respuesta del asistente
        
    Returns:
        str: Respuesta formateada
    """
    return (
        "🤖 *RESPUESTA DEL ASISTENTE*\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"{response}\n\n"
        "_¿Hay algo más en lo que pueda ayudarte?_"
    )