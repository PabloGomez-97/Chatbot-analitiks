from flask import Blueprint
from utils.product_handlers import fetch_and_save_products_json

products_bp = Blueprint('products', __name__)

@products_bp.route('/update_products', methods=['GET'])
def update_products():
    fetch_and_save_products_json()
    return "✅ Datos de productos actualizados exitosamente", 200
