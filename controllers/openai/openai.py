import openai
from datetime import datetime, timedelta
from controllers.smtp.smtp_utils import notify_executive_smtp
from utils.db_helpers import user_exists
from utils.product_logic import search_products

chat_sessions = {}

""" Es utilizado en -> controllers/openai/chat_mode.py """
def ask_openai(client_id, question, name, company):

    """ Palabras clave para detectar si el usuario necesita una cotización """
    keywords_quote = [
        "presupuesto", "cotización", "precio", "costo", "cuánto cuesta", "valores", "oferta", 
        "tarifa", "pago", "gasto", "inversión", "compra", "cuánto vale", "cuál es el costo",
        "coste", "estimado", "propuesta", "plan de pago", "detalles de precio", 
        "cuánto debo pagar", "valor", "monto", "importe", "consulta de precios", "factura",
        "precios actualizados", "descuento", "rebaja", "precio especial", "paquete", 
        "promoción", "cuánto sería", "precio aproximado", "detalles del costo"
    ]

    """ Palabras clave para detectar si el usuario necesita un ejecutivo """
    keywords_human = [
        "contacto", "hablar con alguien", "asistencia", "ayuda real", "soporte humano", 
        "asesor", "consultar con alguien", "asistente real", "llamar", "cómo contactar",
        "quiero hablar", "comunicarme", "teléfono", "representante", "consultor",
        "hablar con un humano", "necesito hablar con un humano", "atención humana", "quiero un humano",
        "persona", "vendedor", "quiero hablar con alguien", "quiero hablar con un vendedor", "técnico", 
        "quiero hablar con un técnico", "quiero hablar con un asesor", "quiero hablar con un consultor"
    ]

    """ Palabras clave para detectar si el usuario busca productos """
    keywords_product = [
        "producto", "necesito", "busco", "quisiera", "ofrecen", "dispositivos", "equipos",
        "sensores", "medidores", "herramientas", "catálogo", "análisis", "tecnología",
        "productos disponibles", "qué productos tienen", "qué ofrecen"
    ]

    # Verificar si el cliente tiene una sesión activa
    if client_id not in chat_sessions or chat_sessions[client_id]['last_interaction'] < datetime.now() - timedelta(minutes=5):
        chat_sessions[client_id] = {'history': [], 'last_interaction': datetime.now()}
    
    chat_sessions[client_id]['last_interaction'] = datetime.now()
    
    # Preparar historial para OpenAI
    history = chat_sessions[client_id]['history']
    messages = [{"role": "system", "content": "Eres un asistente de ventas que ayuda a resolver dudas de dispositivos de medición enfocado en la empresa Analitiks."}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})
    
    """ Si el usuario pregunta por productos, buscar en productos.json """
    if any(keyword in question.lower() for keyword in keywords_product):
        product_results = search_products(question)

        if product_results:
            response_message = "Encontré algunos productos que podrían interesarte, además de otros que podrían ser relevantes:\n\n"
            for product in product_results[:5]:
                response_message += f"- {product['title']}: {product.get('url', 'No disponible')}\n"
            response_message += "\nSi necesitas más información, no dudes en pedírmelo."
            return response_message
        else:
            return "Lo siento, no encontré ningún producto que coincida con tu consulta. Por favor, danos más detalles."

    """ Si el usuario pregunta por una cotización, notificar a un ejecutivo """
    if any(keyword in question.lower() for keyword in keywords_quote):
        name, company = user_exists(client_id)
        notify_executive_smtp(client_id, name, company, question)
        return (
            "Le hemos notificado a uno de nuestros asesores para que se ponga en contacto con usted a la brevedad.\n\n"
            "En el caso que necesite atención inmediata, favor contactar a nuestros canales directos:\n"
            "📞 Número de teléfono: +56 9 9918 5050 o +56 9 9799 8501 \n"
            "📧 Correo electrónico: alfredo.matus@analitiks.cl ó sebastian.alfaro@analitiks.cl"
        )

    """ Si el usuario pregunta por un ejecutivo, notificar a un ejecutivo """
    if any(keyword in question.lower() for keyword in keywords_human):
        return (
            "Le hemos notificado a uno de nuestros asesores para que se ponga en contacto con usted a la brevedad.\n\n"
            "En el caso que necesite atención inmediata, favor contactar a nuestros canales directos:\n"
            "📞 Número de teléfono: +56 9 9918 5050 o +56 9 9799 8501 \n"
            "📧 Correo electrónico: alfredo.matus@analitiks.cl ó sebastian.alfaro@analitiks.cl"
        )
    
    try:
        # Procesar mensaje con OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        answer = response['choices'][0]['message']['content'].strip()

        # Actualizar historial del chat
        chat_sessions[client_id]['history'].append({"role": "user", "content": question})
        chat_sessions[client_id]['history'].append({"role": "assistant", "content": answer})
        
        return answer
    
    except Exception as e:
        return (
            "Hubo un error al procesar tu solicitud. Por favor, contacta al número +56 9 9918 5050 o +56 9 9799 8501 "
            "o al correo info@analitiks.cl para asistencia."
        )
