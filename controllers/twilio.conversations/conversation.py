from twilio.rest import Client
import os
import threading

def handle_option_7(user_number, response):
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        conversation_sid = os.getenv('TWILIO_CONVERSATION_SID')

        client = Client(account_sid, auth_token)
        participants = client.conversations \
                             .v1 \
                             .conversations(conversation_sid) \
                             .participants \
                             .list()

        if not any(p.identity == user_number for p in participants):
            client.conversations \
                  .v1 \
                  .conversations(conversation_sid) \
                  .participants \
                  .create(identity=user_number)

        client.conversations \
              .v1 \
              .conversations(conversation_sid) \
              .messages \
              .create(author="system", body="¡Espéranos en línea mientras buscamos un agente! 🙌")

        def delayed_response():
            response.message(
                "👨‍💼 Ahora estás conectado con un ejecutivo. Escribe tu mensaje y te responderemos en breve."
            )

        # Crear un hilo para manejar el retraso
        threading.Timer(10, delayed_response).start()

    except Exception as e:
        print(f"Error al conectar al cliente con un humano: {str(e)}")
        response.message(
            "⚠️ Lo sentimos, ocurrió un problema al conectarte con un representante. Por favor, intenta de nuevo más tarde."
        )
