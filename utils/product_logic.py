import json

def load_products():
    """Carga los productos desde el archivo productos.json."""
    try:
        with open("productos.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def search_products(query):
    """
    Busca productos relevantes en productos.json basados en la consulta del usuario.
    Parámetros:
        - query: Cadena de texto ingresada por el usuario.
    Retorna:
        - Una lista de productos que coinciden con la consulta.
    """
    products = load_products()
    results = []

    for product in products:
        if query.lower() in product['title'].lower() or query.lower() in product.get('description', '').lower():
            results.append(product)
    
    return results
