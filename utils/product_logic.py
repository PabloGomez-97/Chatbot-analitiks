import json

def load_products():
    """
    Carga los productos desde el archivo productos.json.
    """
    try:
        with open("productos.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # Cargar el JSON como un objeto Python
            
            # Acceder a la clave "products"
            products = data.get("products", [])
            
            if not isinstance(products, list):  # Verificar que sea una lista
                raise ValueError("El archivo JSON no tiene el formato esperado: 'products' no es una lista.")
            return products
    except Exception as e:
        print(f"Error al cargar productos: {e}")
        return []



def search_products(query):
    """
    Busca productos relevantes en productos.json basados en la consulta del usuario.
    """
    products = load_products()  # Cargar productos desde productos.json
    results = []

    # Normalizar la consulta del usuario
    query_words = query.lower().strip().split()  # Dividir la consulta en palabras

    for product in products:
        if not isinstance(product, dict):  # Ignorar productos mal formateados
            continue
        
        # Normalizar título y descripción del producto
        title = product.get("title", "").lower().strip()
        description = product.get("description", "").lower().strip()

        # Verificar si alguna palabra de la consulta está en el título o descripción
        if any(word in title or word in description for word in query_words):
            results.append(product)

    return results

