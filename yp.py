def handle_option_7(user_number, response):
    """
    Conecta al cliente con un humano a través de Twilio Conversations.
    """
    try:
        # Configuración de Twilio
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        conversation_sid = os.getenv('TWILIO_CONVERSATION_SID')  # SID de la conversación
        client = Client(account_sid, auth_token)

        # Agregar al cliente como participante si no está ya agregado
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

        # Cambiar el estado del usuario a 'executive_mode'
        user_state[user_number] = 'executive_mode'

        # Enviar un mensaje inicial al cliente
        client.conversations \
              .v1 \
              .conversations(conversation_sid) \
              .messages \
              .create(author="system", body="Te hemos conectado con un representante humano. Por favor, espera mientras te respondemos.")

        # Responder al cliente en WhatsApp
        response.message(
            "👨‍💼 Ahora estás conectado con un humano. Si deseas salir de la conversación, escribe 'salir'."
        )
        return str(response)

    except Exception as e:
        print(f"Error en la opción 7: {str(e)}")
        response.message(
            "⚠️ Lo sentimos, ocurrió un problema al conectarte con un representante. Por favor, intenta de nuevo más tarde."
        )
        return str(response)
