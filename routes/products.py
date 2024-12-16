from flask import Blueprint
from utils.producthandlers import fetch_and_save_products_json

products_bp = Blueprint('products', __name__)

def update_products():
    fetch_and_save_products_json()
    return "✅ Datos de productos actualizados exitosamente", 200
