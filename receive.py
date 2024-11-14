import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import time
from threading import Timer
import mysql.connector
import json
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Configuración de la clave API de OpenAI
openai.api_key = 'tu_clave_openai'

# Diccionarios para rastrear el estado del usuario y temporizadores de inactividad
last_interaction_time = {}
timers = {}
user_state = {}

# Configuración de conexión a MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="crm_user",
        password="crm_password",
        database="crm_db",
        port=3306
    )

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

# Función para obtener información de productos desde productos.json
def get_product_info(product_name):
    try:
        with open('productos.json') as file:
            products = json.load(file)["products"]
        for product in products:
            if product_name.lower() == product["title"].lower():
                return (f"🔹 *{product['title']}*\n"
                        f"🔗 [Ver producto]({product['url']})\n"
                        f"🖼️ Imagen: {product['image']}")
        return "Lo siento, no encontré un producto con ese nombre. Asegúrate de escribir el nombre exacto."
    except FileNotFoundError:
        return "No se encontró el archivo de productos. Por favor, actualízalo usando la ruta /update_products."

# Función para hacer preguntas a OpenAI
def ask_openai(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
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
        if current_time - last_interaction_time[user_number] > 300:
            print(f"Despedida enviada a {user_number}")
            last_interaction_time.pop(user_number, None)
            if user_number in timers:
                timers[user_number].cancel()
                timers.pop(user_number, None)

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

def fetch_and_save_products_json():
    # URL base de la página de productos con paginación
    base_url = "https://analitiks.cl/categoria-producto/productos/page/{}/"
    page = 1
    products = []

    while True:
        # Solicita cada página de productos
        response = requests.get(base_url.format(page))
        if response.status_code != 200:
            print(f"Final de las páginas alcanzado o error en la página {page}. Código de estado: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.content, "html.parser")
        product_elements = soup.select("ul.products li.product")

        # Si no hay productos en la página, salir del bucle
        if not product_elements:
            print(f"No se encontraron más productos en la página {page}.")
            break

        # Extraer datos de cada producto en la página
        for product in product_elements:
            product_data = {
                "title": product.select_one("h2.woocommerce-loop-product__title").text.strip(),
                "url": product.select_one("a.woocommerce-LoopProduct-link")["href"],
                "image": product.select_one("img")["src"],
                "categories": [cat.text.strip() for cat in product.select(".product_cat-inmersion, .product_cat-porta-sensores, .product_cat-productos")]
            }
            products.append(product_data)
        
        print(f"Productos obtenidos de la página {page}.")
        page += 1  # Incrementar el número de página para continuar

    # Guardar todos los productos en productos.json
    with open("productos.json", "w", encoding="utf-8") as file:
        json.dump({"products": products}, file, ensure_ascii=False, indent=4)
    
    print("Todos los productos han sido guardados en productos.json")


@app.route('/update_products', methods=['GET'])
def update_products():
    fetch_and_save_products_json()
    return "Datos de productos actualizados y guardados en productos.json", 200

# Endpoint principal para recibir y responder mensajes de WhatsApp
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_message = request.values.get('Body', '').strip()
    user_number = request.values.get('From').replace('whatsapp:', '')

    response = MessagingResponse()
    last_interaction_time[user_number] = time.time()

    # Reiniciar temporizador de inactividad
    if user_number in timers:
        timers[user_number].cancel()
    timers[user_number] = Timer(300, inactivity_warning, args=[user_number])
    timers[user_number].start()

    # Verificar si el usuario ya existe
    user = user_exists(user_number)

    # Flujo de registro
    if not user:
        if user_number not in user_state:
            user_state[user_number] = 'awaiting_name'
            response.message("👋 ¡Bienvenido a Analitiks! Antes de continuar, por favor ingresa tu *nombre*.")
        elif user_state[user_number] == 'awaiting_name':
            user_state[user_number] = 'awaiting_company'
            user_state['name'] = incoming_message
            response.message("Gracias, ahora por favor ingresa el nombre de tu *empresa*.")
        elif user_state[user_number] == 'awaiting_company':
            name = user_state.pop('name')
            save_user(user_number, name, incoming_message)
            user_state[user_number] = 'registered'
            response.message(f"¡Gracias {name}! ¿Cómo puedo ayudarte hoy?\n\n"
                             "1️⃣ *¿Quiénes somos?*\n"
                             "2️⃣ *Contacto*\n"
                             "3️⃣ *Asistente técnico (IA)*\n"
                             "4️⃣ *Ver historial completo*\n"
                             "5️⃣ *Finalizar conversación*\n"
                             "6️⃣ *Información de productos*\n")
        return str(response)

    # Verificar si el usuario está en modo de información de productos
    if user_state.get(user_number) == 'product_info':
        # Procesar el nombre del producto y mostrar la información
        product_info = get_product_info(incoming_message)
        save_message(user_number, product_info, 'Bot')
        response.message(product_info)
        # Restablecer el estado del usuario para que regrese al menú principal después de recibir la información del producto
        user_state[user_number] = 'menu_shown'
        return str(response)

    # Mostrar menú de opciones si el mensaje es "Hola" o no coincide con ninguna opción
    name, company = user
    if incoming_message.lower() == "hola" or incoming_message not in ['1', '2', '3', '4', '5', '6']:
        response.message(f"Hola {name} de {company}, ¿cómo podemos ayudarte hoy?\n\n"
                         "1️⃣ *¿Quiénes somos?*\n"
                         "2️⃣ *Contacto*\n"
                         "3️⃣ *Asistente técnico (IA)*\n"
                         "4️⃣ *Ver historial completo*\n"
                         "5️⃣ *Finalizar conversación*\n"
                         "6️⃣ *Información de productos*\n")
    else:
        # Flujo de opciones para usuario registrado
        if incoming_message == '1':
            response.message("Analitiks es la única compañía nacional 100% dedicada a entregar la más alta tecnología de análisis en línea para procesos industriales en Chile.")
        elif incoming_message == '2':
            response.message("Contáctanos en: contacto@analitiks.cl o en www.analitiks.cl.")
        elif incoming_message == '3':
            user_state[user_number] = 'assistant_mode'
            response.message("¿Cuál es tu duda técnica? Pregunta lo que necesites saber, nuestro asistente técnico con IA te ayudará.")
        elif incoming_message == '4':
            responses = get_user_responses(user_number)
            historial = "\n".join([f"[{timestamp}] {sender}: {message}" for message, sender, timestamp in responses]) or "No tienes historial."
            response.message(historial)
        elif incoming_message == '5':
            response.message("Gracias por conversar con Analitiks. ¡Hasta luego!")
            del last_interaction_time[user_number]
            timers[user_number].cancel()
            del timers[user_number]
            user_state.pop(user_number, None)
        elif incoming_message == '6':
            response.message("¿Qué producto te interesa? Por favor, ingresa el nombre exacto del producto.")
            user_state[user_number] = 'product_info'

    save_message(user_number, incoming_message, 'User')
    return str(response)

if __name__ == '__main__':
    app.run(port=8080)
