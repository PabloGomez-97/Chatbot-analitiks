import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import sqlite3
import time
from threading import Timer
import mysql.connector

app = Flask(__name__)

# Configura tu clave API de OpenAI
openai.api_key = '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'

# Diccionario para rastrear el tiempo de inactividad
last_interaction_time = {}
timers = {}
# Diccionario para rastrear el estado del usuario (en qué parte del flujo está)
user_state = {}

# Configuración de conexión a MySQL
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",  # O usa el nombre de tu contenedor si usas Docker Compose, como 'db'
        user="crm_user",
        password="crm_password",
        database="crm_db",
        port=3306
    )
    return conn

# Función para guardar mensajes en la base de datos
def save_message(user_number, message, sender):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (user_number, message, sender) VALUES (%s, %s, %s)", (user_number, message, sender))
    conn.commit()
    cursor.close()
    conn.close()

# Función para obtener mensajes anteriores de la base de datos
def get_user_responses(user_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT message, sender, timestamp FROM conversations WHERE user_number = %s ORDER BY timestamp", (user_number,))
    responses = cursor.fetchall()
    cursor.close()
    conn.close()
    return responses

# Función para hacer preguntas a OpenAI
def ask_openai(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Puedes usar "gpt-4" si tienes acceso
        messages=[
            {"role": "system", "content": "Eres un asistente técnico que ayuda a resolver problemas técnicos de dispositivos de medición."},
            {"role": "user", "content": question}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()

# Función para manejar la inactividad del usuario
def inactivity_warning(user_number):
    if user_number in last_interaction_time:
        current_time = time.time()
        if current_time - last_interaction_time[user_number] > 300:  # 300 segundos = 5 minutos
            print(f"Despedida enviada a {user_number}")  # Aquí puedes agregar la lógica para enviar un mensaje de despedida
            del last_interaction_time[user_number]
            del timers[user_number]

# Función para verificar si el usuario ya existe
def user_exists(user_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, company FROM users WHERE user_number = %s", (user_number,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Función para guardar el nombre y la empresa del usuario
def save_user(user_number, name, company):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_number, name, company) VALUES (%s, %s, %s)", (user_number, name, company))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_message = request.values.get('Body', '').strip()
    user_number = request.values.get('From')
    if user_number.startswith('whatsapp:'):
        user_number = user_number.replace('whatsapp:', '')
    response = MessagingResponse()

    # Actualizar el tiempo de la última interacción
    last_interaction_time[user_number] = time.time()

    # Cancelar temporizadores antiguos y reiniciar el temporizador
    if user_number in timers:
        timers[user_number].cancel()
    timers[user_number] = Timer(300, inactivity_warning, args=[user_number])  # 5 minutos
    timers[user_number].start()

    if user_state.get(user_number) == 'assistant_mode':
        openai_response = ask_openai(incoming_message)  # Pregunta a la API de OpenAI
        save_message(user_number, openai_response, 'Bot')  # Guardar la respuesta en la base de datos
        response.message(openai_response)  # Enviar la respuesta al usuario
        return str(response)

    # Verificar si el usuario ya existe
    user = user_exists(user_number)

    # Si el usuario es nuevo, pedir nombre y empresa
    if not user:
        if user_number not in user_state:
            # Primer mensaje: pedir el nombre
            user_state[user_number] = 'awaiting_name'
            response.message("👋 ¡Bienvenido a Analitiks! Antes de continuar, por favor ingresa tu *nombre*.")
        elif user_state[user_number] == 'awaiting_name':
            # Almacenar el nombre y pedir la empresa
            user_state[user_number] = 'awaiting_company'
            user_state['name'] = incoming_message
            response.message("Gracias, ahora por favor ingresa el nombre de tu *empresa*.")
        elif user_state[user_number] == 'awaiting_company':
            # Almacenar la empresa, registrar el usuario y mostrar las opciones
            name = user_state.pop('name')
            company = incoming_message
            save_user(user_number, name, company)
            user_state[user_number] = 'registered'
            response.message(f"¡Gracias {name}! Ya estás registrado. ¿Cómo puedo ayudarte hoy?\n\n"
                             "1️⃣ *¿Quiénes somos?* - Conoce más sobre nosotros y nuestra misión.\n"
                             "2️⃣ *¿Qué hacemos?* - Descubre nuestras soluciones tecnológicas.\n"
                             "3️⃣ *Mercados que atendemos* - Sectores donde nuestra tecnología hace la diferencia.\n"
                             "4️⃣ *Contacto* - ¿Necesitas hablar con nosotros? ¡Estamos aquí para ti!\n"
                             "5️⃣ *Asistente técnico inteligente (IA)* 🤖 - Obtén ayuda técnica especializada al instante.\n"
                             "6️⃣ *Ver historial completo* - Revisa toda tu conversación con nosotros.\n"
                             "7️⃣ *Finalizar conversación* - Cierra el chat cuando hayas terminado.\n\n"
                             "✨ ¡Estamos listos para ayudarte a transformar tus procesos con tecnología de vanguardia!")
            user_state[user_number] = 'menu_shown'

    # Si el usuario ya existe, saludarlo una vez y no volver a mostrar el menú cada vez
    name, company = user
    if user_number not in user_state or user_state[user_number] != 'menu_shown':
        response.message(f"Hola {name} de {company}, ¿cómo podemos ayudarte hoy?\n\n"
                         "1️⃣ *¿Quiénes somos?* - Conoce más sobre nosotros y nuestra misión.\n"
                         "2️⃣ *¿Qué hacemos?* - Descubre nuestras soluciones tecnológicas.\n"
                         "3️⃣ *Mercados que atendemos* - Sectores donde nuestra tecnología hace la diferencia.\n"
                         "4️⃣ *Contacto* - ¿Necesitas hablar con nosotros? ¡Estamos aquí para ti!\n"
                         "5️⃣ *Asistente técnico inteligente (IA)* 🤖 - Obtén ayuda técnica especializada al instante.\n"
                         "6️⃣ *Ver historial completo* - Revisa toda tu conversación con nosotros.\n"
                         "7️⃣ *Finalizar conversación* - Cierra el chat cuando hayas terminado.\n\n"
                         "✨ ¡Estamos listos para ayudarte a transformar tus procesos con tecnología de vanguardia!")
        user_state[user_number] = 'menu_shown'

    # Guardar el mensaje del usuario
    save_message(user_number, incoming_message, name)

    # Verificar si el usuario está en el flujo de "Asistente técnico inteligente"
    if user_number in user_state and user_state[user_number] == 'assistant_mode':
        openai_response = ask_openai(incoming_message)  # Pregunta a la API de OpenAI
        save_message(user_number, openai_response, 'Bot')  # Guardar la respuesta en la base de datos
        response.message(openai_response)  # Enviar la respuesta al usuario
        return str(response)


    # Manejo de otras opciones
    if incoming_message == '1':
        bot_message = "Analitiks es la única compañía nacional 100% dedicada a entregar la más alta tecnología de análisis en línea para procesos industriales en Chile. Ofrecemos soluciones personalizadas, servicio técnico y capacitación."
        save_message(user_number, bot_message, 'Bot')
        response.message(bot_message)
    elif incoming_message == '2':
        bot_message = "En Analitiks, brindamos soluciones para la medición y monitoreo de fluidos en tiempo real. Nuestro enfoque está en la automatización y análisis en línea para diversos sectores industriales."
        save_message(user_number, bot_message, 'Bot')
        response.message(bot_message)
    elif incoming_message == '3':
        bot_message = "Atendemos los sectores de minería, energía, pulpa y papel, alimentos y bebidas, entre otros. Somos expertos en tecnologías para análisis de procesos industriales."
        save_message(user_number, bot_message, 'Bot')
        response.message(bot_message)
    elif incoming_message == '4':
        bot_message = "Para más información, puedes contactarnos en: contacto@analitiks.cl o visitar nuestro sitio web en www.analitiks.cl."
        save_message(user_number, bot_message, 'Bot')
        response.message(bot_message)
    elif incoming_message == '5':
        bot_message = "¿Cuál es tu duda técnica? Pregunta lo que necesites saber, nuestro asistente técnico con IA te ayudará."
        save_message(user_number, bot_message, 'Bot')
        response.message(bot_message)
        user_state[user_number] = 'assistant_mode'
    elif incoming_message == '6':
        previous_responses = get_user_responses(user_number)
        if previous_responses:
            historial_completo = "Este es tu historial completo de conversaciones:\n"
            historial_completo += "\n".join([f"[{timestamp}] {sender}: {message}" for message, sender, timestamp in previous_responses])
            response.message(historial_completo)
        else:
            response.message("No tienes historial de conversaciones previo.")
    elif incoming_message == '7':
        response.message("Gracias por conversar con Analitiks. ¡Hasta luego!")
        del last_interaction_time[user_number]
        timers[user_number].cancel()
        del timers[user_number]
        user_state.pop(user_number, None)  # Limpiar el estado del usuario
    
    return str(response)

if __name__ == '__main__':
    app.run(port=8080)
