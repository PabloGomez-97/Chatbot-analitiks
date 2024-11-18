import json
import requests
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
            product_data = {
                "title": product.select_one("h2.woocommerce-loop-product__title").text.strip(),
                "url": product.select_one("a.woocommerce-LoopProduct-link")["href"],
                "image": product.select_one("img")["src"],
                "categories": [cat.text.strip() for cat in product.select(".product_cat-inmersion, .product_cat-porta-sensores, .product_cat-productos")]
            }
            products.append(product_data)

        print(f"Productos obtenidos de la página {page}.")
        page += 1

    with open("productos.json", "w", encoding="utf-8") as file:
        json.dump({"products": products}, file, ensure_ascii=False, indent=4)
    
    print("Todos los productos han sido guardados en productos.json")


# Función para obtener información de productos desde productos.json
def get_product_info(product_name):
    try:
        with open('productos.json') as file:
            products = json.load(file)["products"]
        for product in products:
            if product_name.lower() == product["title"].lower():
                return (f"🔹 *{product['title']}*\n"
                        f"🔗 [Ver producto]({product['url']})\n"
                        f"🖼️ Description: {product['description']}")
        return "Lo siento, no encontré un producto con ese nombre. Asegúrate de escribir el nombre exacto."
    except FileNotFoundError:
        return "No se encontró el archivo de productos. Por favor, actualízalo usando la ruta /update_products."