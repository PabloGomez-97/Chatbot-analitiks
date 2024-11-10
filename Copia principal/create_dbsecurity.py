import sqlite3

# Conexión a la base de datos (se crea si no existe)
conn = sqlite3.connect('user_responses.db')
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS conversations (
    user_number TEXT,
    message TEXT,
    sender TEXT,  -- Nueva columna para identificar quién envió el mensaje
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Si la tabla ya existía, agregar la columna 'sender' si aún no está presente
# Esto es útil si la tabla fue creada sin esta columna anteriormente
try:
    cursor.execute("ALTER TABLE conversations ADD COLUMN sender TEXT")
except sqlite3.OperationalError:
    # La columna ya existe, así que no hacemos nada
    pass

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()
