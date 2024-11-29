# Usar una imagen base de Python
FROM python:3.9-slim

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt y luego instalar dependencias (optimiza la caché de Docker)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto al contenedor
COPY . /app

# Exponer el puerto para la aplicación Flask
EXPOSE 9090

# Configurar variables de entorno para logs en tiempo real
ENV PYTHONUNBUFFERED=1

# Comando para iniciar la aplicación
CMD ["python", "receive.py"]
