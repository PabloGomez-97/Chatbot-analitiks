# WhatsApp Bot con Gestión de Usuarios y Notificaciones

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0-lightgrey)
![Twilio](https://img.shields.io/badge/Twilio-API-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange)

Este proyecto implementa un **bot de WhatsApp** utilizando Flask, Twilio y OpenAI para gestionar la interacción con los usuarios, ofrecer flujos personalizados y enviar notificaciones por correo electrónico. Incluye funcionalidades como:
- Gestión de usuarios registrados y no registrados.
- Historial de conversaciones almacenado y recuperado dinámicamente.
- Modo asistente con respuestas basadas en OpenAI.
- Notificaciones automatizadas por correo utilizando Mailgun.

## Tabla de Contenidos
- [Instalación](#instalación)
- [Características](#características)
- [Endpoints](#endpoints)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Uso](#uso)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

---

## Instalación

1. **Clona este repositorio:**
   ```bash
   git clone https://github.com/tuusuario/whatsapp-bot.git
   cd whatsapp-bot
   ```

2. **Crea y activa un entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno:**
   - Crea un archivo `.env` en la raíz del proyecto:
     ```bash
     touch .env
     ```
   - Agrega las siguientes variables:
     ```plaintext
     OPENAI_API_KEY=tu_clave_de_openai
     MAILGUN_SMTP_USER=postmaster@tu-dominio
     MAILGUN_SMTP_PASSWORD=tu_contraseña
     ```

5. **Inicia el servidor:**
   ```bash
   python app.py
   ```

---

## Características

- **Gestión de usuarios**:
  - Soporte para usuarios registrados y no registrados.
  - Menú dinámico basado en el estado del usuario.

- **Modo asistente**:
  - Respuestas automáticas utilizando OpenAI.

- **Historial de conversaciones**:
  - Almacenamiento y recuperación de mensajes de los usuarios.

- **Notificaciones por correo**:
  - Correo automático al ejecutivo con el historial del cliente.

- **Actualización dinámica de productos**:
  - Endpoint para sincronizar productos en la base de datos.

---

## Endpoints

### 1. `/update_products`
- **Método**: `GET`
- **Descripción**: Actualiza la base de datos con los últimos productos.

### 2. `/getusers`
- **Método**: `GET`
- **Descripción**: Obtiene todos los usuarios registrados.

### 3. `/getleads`
- **Método**: `GET`
- **Descripción**: Obtiene usuarios registrados en las últimas 24 horas.

### 4. `/getmessages`
- **Método**: `GET`
- **Parámetros**: `user_number`
- **Descripción**: Recupera el historial de mensajes de un usuario.

### 5. `/whatsapp`
- **Método**: `POST`
- **Descripción**: Endpoint principal para manejar mensajes de WhatsApp.

---

## Estructura del Proyecto

```plaintext
whatsapp-bot/
├── app.py                  # Archivo principal de la aplicación Flask
├── utils/
│   ├── product_fetcher.py  # Funciones para sincronizar productos
│   ├── db_helpers.py       # Interacciones con la base de datos
│   ├── message_formatter.py # Formateo de mensajes
│   ├── user_handlers.py    # Lógica de manejo de usuarios
│   ├── product_handlers.py # Manejo de opciones de productos
├── controllers/
│   ├── openai/
│   │   └── chat_mode.py    # Lógica del modo asistente basado en OpenAI
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Documentación del proyecto
├── .env                    # Variables de entorno (excluido en .gitignore)
└── HTML/
    └── email_template.html # Plantilla de correo HTML
```

---

## Uso

1. **Interacción en WhatsApp:**
   - Registra tu número en Twilio y configura el webhook para que apunte al endpoint `/whatsapp`.

2. **Personalización:**
   - Edita las plantillas de correos en el directorio `HTML/` para adaptarlas a tus necesidades.
   - Modifica las funciones de respuesta en `message_formatter.py`.

3. **Pruebas locales:**
   - Usa `ngrok` para exponer el servidor Flask a internet:
     ```bash
     ngrok http 9090
     ```
   - Configura el webhook de Twilio con la URL pública de ngrok.

---

## Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar este proyecto:
1. Haz un fork del repositorio.
2. Crea una rama con tus cambios:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. Realiza un pull request.

---

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

¡Gracias por usar este bot! 🚀

--- 

Con este README, tus colaboradores y usuarios tendrán una guía clara para entender, instalar y contribuir al proyecto.
