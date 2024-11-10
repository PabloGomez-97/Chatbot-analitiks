from twilio.rest import Client

# Tus credenciales SID y Token
account_sid = 'AC52a802cfcdbb7852fc0684d8c68c385c'
auth_token = '3f5a5a9461aee7c93d006345486940c5'
client = Client(account_sid, auth_token)

# Configura los números de WhatsApp
from_whatsapp_number = 'whatsapp:+14155238886'
to_whatsapp_number = 'whatsapp:+56992193809'

# Aquí puedes personalizar el mensaje que deseas enviar
message_body = "Hola, este es tu mensaje personalizado!"

# Envía el mensaje con el cuerpo personalizado
message = client.messages.create(
    body=message_body,
    from_=from_whatsapp_number,
    to=to_whatsapp_number
)

# Imprime el SID del mensaje enviado
print(f"Message sent with SID: {message.sid}")
