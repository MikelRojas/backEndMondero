import mysql.connector
from datetime import datetime
from flask import jsonify

def sign_in_verification_nodo(name, password):
    conexion = mysql.connector.connect(
        host="localhost",         # Cambia esto si tu MySQL está en otro servidor
        user="root",              # Tu nombre de usuario de MySQL
        password="marr5604",      # Tu contraseña de MySQL
        database="server_central" # El nombre de la base de datos a la que quieres acceder
    )
    
    cursor = conexion.cursor()
    cursor.execute(f"SELECT id FROM nodos WHERE nombre_nodo_local = %s AND password = %s", (name, password))
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    if len(resultados) == 0:
        return jsonify({"id": 0})  # No se encontró el nodo
    return jsonify({"id": resultados[0][0]})  # Retorna el id del nodo encontrado

def verification_client(id):
    conexion = mysql.connector.connect(
        host="localhost",         # Cambia esto si tu MySQL está en otro servidor
        user="root",              # Tu nombre de usuario de MySQL
        password="marr5604",      # Tu contraseña de MySQL
        database="server_central" # El nombre de la base de datos a la que quieres acceder
    )
    
    cursor = conexion.cursor()
    cursor.execute(f"SELECT id FROM clientes WHERE id = %s", (id))
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    if len(resultados) == 0:
        return jsonify({"id": 0}) 
    return jsonify({"id": resultados[0][0]})  # Retorna el id del nodo encontrado


def verification_client_PWA(name, email, phone, password):
    conexion = mysql.connector.connect(
        host="localhost",  # Cambia esto si tu MySQL está en otro servidor
        user="root",  # Tu nombre de usuario de MySQL
        password="marr5604",  # Tu contraseña de MySQL
        database="server_central"  # El nombre de la base de datos a la que quieres acceder
    )

    cursor = conexion.cursor()
    # Consulta para verificar si existe un cliente con el nombre, correo y teléfono
    query = "SELECT id FROM clientes WHERE nombre = %s AND correo = %s AND telefono = %s AND contrasena = %s"
    cursor.execute(query, (name, email, phone,password))

    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Si no se encuentran resultados, se retorna un id = 0
    if len(resultados) == 0:
        return jsonify({"id": 0})  # No se encontró el cliente

    # Si se encontró el cliente, se retorna el id del cliente
    return jsonify({"id": resultados[0][0]})

# Aquí puedes definir la función para obtener el saldo del cliente
def get_client_balance(client_id):
    # Aquí iría la lógica para obtener el saldo del cliente desde la base de datos
    # Ejemplo:
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="marr5604",
        database="server_central"
    )
    cursor = conexion.cursor()

    # Consulta para obtener el saldo del cliente
    query = "SELECT saldo FROM monedero_electronico WHERE cliente_id = %s"
    cursor.execute(query, (client_id,))
    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    if resultado:
        return resultado[0]  # Retorna el saldo
    return 0  # Si no se encuentra el saldo, retorna 0


def recargar_monedero(cliente_id, monto):
    try:
        # Conectar a la base de datos MySQL
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="marr5604",
            database="server_central"
        )
        
        cursor = conexion.cursor()

        # Llamar al procedimiento almacenado 'recargar_monedero'
        cursor.callproc('recargar_monedero', [cliente_id, float(monto)])

        # Confirmar la transacción
        conexion.commit()

        cursor.close()
        conexion.close()

        return jsonify({"success": True, "message": "Recarga realizada con éxito"})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": str(err)})
    
def register_nodo(nombre_nodo, password):
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="marr5604",
            database="server_central"
        )
        
        cursor = conexion.cursor()
        cursor.execute(f"INSERT INTO nodos (nombre_nodo_local, password) VALUES ('{nombre_nodo}', '{password}')")
        cursor.close()
        conexion.close()
        return True
    except mysql.connector.Error as err:
        return False

def insertar_promocion(descripcion, porcentaje_descuento, nodo_id, fecha_fin):
    try:
        # Conectar a la base de datos MySQL
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="marr5604",
            database="server_central"
        )
        
        cursor = conexion.cursor()

        # Fecha actual para la fecha de inicio
        fecha_inicio = datetime.now()

        # Consulta para insertar la promoción
        query = """
        INSERT INTO promociones (descripcion, porcentaje_descuento, nodo_id, fecha_inicio, fecha_fin)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        # Si el nodo_id es None, establece NULL
        if nodo_id is None:
            cursor.execute(query, (descripcion, porcentaje_descuento, None, fecha_inicio, fecha_fin))
        else:
            cursor.execute(query, (descripcion, porcentaje_descuento, nodo_id, fecha_inicio, fecha_fin))
        
        # Confirmar la transacción
        conexion.commit()

        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()

        return jsonify({"success": True, "message": "Promoción insertada con éxito"})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": str(err)})

