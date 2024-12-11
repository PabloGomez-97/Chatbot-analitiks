from .message_formatter import format_product_info #
from utils.message_formatter import create_menu_message
from .db_helpers import save_message #
import json
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

def handle_product_search_options(user_number, incoming_message, response, user, user_state):
    name, company = user
    if incoming_message == '1':
        user_state[user_number] = 'product_info'
        """ Opción 1: Cambia el estado a 'product_info' y redirige a la lógica en utils.product_handlers.py -> handle_specific_product_info. """
        response.message(
            "Por favor, ingresa el nombre exacto del producto que estás buscando"
        )
    elif incoming_message == '2':
        user_state[user_number] = 'assistant_mode'
        """ Opción 2: Cambia el estado a 'assistant_mode' y redirige a la lógica en openai.chat_mode.py -> handle_assistant_mode. """
        response.message(
            "Describe el producto que necesitas y te ayudaré a encontrarlo"
        )
    else:
        response.message(
            "⚠️ *Opción no válida*\n\n"
            "Por favor selecciona:\n"
            "1️⃣ *Conozco el nombre del producto*\n"
            "2️⃣ *No conozco el nombre del producto*"
        )
    return str(response)


"""" Es utilizado en -> utils/product_handler.py """
def get_product_info(product_name):
    try:
        with open('productos.json', encoding="utf-8") as file:
            products = json.load(file)["products"]
        for product in products:
            if product_name.lower() == product["title"].lower():
                ficha_tecnica_msg = (f"📑 [Ficha técnica]({product['ficha_tecnica']})" 
                                     if product['ficha_tecnica'] 
                                     else "📑 Ficha técnica no disponible.")
                return (f"🔹 *{product['title']} {product['url']}*\n"
                        f"📂 Categorías: {', '.join(product['categories'])}\n"
                        f"{ficha_tecnica_msg}\n"
                        f"📄 {product['description']}\n")
        return "Lo siento, no encontré un producto con ese nombre. Asegúrate de escribir el nombre exacto."
    except FileNotFoundError:
        return "No se encontró el archivo de productos. Por favor, actualízalo usando la ruta /update_products."


""" Es utilizado en -> utils/product_handlers.py opción 1"""
def handle_specific_product_info(user_number, incoming_message, response, user_state, name, company):
    if incoming_message.lower() == "salir":
        user_state.pop(user_number, None)
        response.message(create_menu_message(name, company))
        return str(response)
    
    product_info = get_product_info(incoming_message)
    save_message(user_number, product_info, 'Bot')
    response.message(format_product_info(product_info))
    return str(response)


def fetch_and_save_products_json():
    base_url = "https://analitiks.cl/categoria-producto/productos/page/{}/"
    page = 1
    products = []

    while True:
        response = requests.get(base_url.format(page))
        if response.status_code != 200:
            print(f"Final de las páginas alcanzado o error en la página {page}. Código de estado: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        product_elements = soup.select("ul.products li.product")

        if not product_elements:
            print(f"No se encontraron más productos en la página {page}.")
            break

        for product in product_elements:
            product_url = product.select_one("a.woocommerce-LoopProduct-link")["href"]
            
            # Fetch the product detail page to extract description, categories, and ficha técnica
            product_response = requests.get(product_url)
            if product_response.status_code != 200:
                print(f"Error al acceder a la página del producto: {product_url}. Código de estado: {product_response.status_code}")
                continue

            product_soup = BeautifulSoup(product_response.content, "html.parser")
            categories = [cat.text.strip() for cat in product_soup.select(".posted_in a")]
            description = product_soup.select_one(".woocommerce-Tabs-panel--description")
            description = description.text.strip() if description else "Descripción no disponible."

            # Extract the URL of the ficha técnica
            ficha_tecnica = product_soup.find("a", string=lambda text: text and "Ficha Técnica" in text)
            ficha_tecnica_url = ficha_tecnica["href"] if ficha_tecnica else None

            # Encode the ficha_tecnica_url
            if ficha_tecnica_url:
                ficha_tecnica_url = quote(ficha_tecnica_url, safe=":/")

            # Add cotizacion field with a cleaner mailto link
            mailto_link = (
                f"mailto:cotizaciones@analitiks.cl?"
                f"subject=Cotización%20producto%20{quote(product.select_one('h2.woocommerce-loop-product__title').text.strip())}&"
                f"body=Hola,%me%interesaría%obtener%una%cotización%de%este%producto.%Por%favor,%indicar%detalles%y%precio."
            )
            cotizacion_message = (
                f"Solicita una cotización aquí: ,({mailto_link})."
            )

            product_data = {
                "title": product.select_one("h2.woocommerce-loop-product__title").text.strip(),
                "url": product_url,
                "categories": categories,
                "description": description,
                "ficha_tecnica": ficha_tecnica_url,
                "cotizacion": cotizacion_message
            }
            products.append(product_data)

        print(f"Productos obtenidos de la página {page}.")
        page += 1

    with open("productos.json", "w", encoding="utf-8") as file:
        json.dump({"products": products}, file, ensure_ascii=False, indent=4)
    
    print("Todos los productos han sido guardados en productos.json")
