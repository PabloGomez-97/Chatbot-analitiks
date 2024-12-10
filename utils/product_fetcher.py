import json
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

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
                        f"📄 {product['description']}\n"
                        f"{product['cotizacion']}")
        return "Lo siento, no encontré un producto con ese nombre. Asegúrate de escribir el nombre exacto."
    except FileNotFoundError:
        return "No se encontró el archivo de productos. Por favor, actualízalo usando la ruta /update_products."

# Utilizar solo en caso de querer actualizar el archivo productos.json
# fetch_and_save_products_json()
