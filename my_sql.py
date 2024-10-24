import mysql.connector
from datetime import datetime
from flask import jsonify

def sign_in_verification_nodo(name, password):
    """Verifica las credenciales de un nodo.

    Args:
        name (str): Nombre del nodo a verificar.
        password (str): Contraseña del nodo.

    Returns:
        jsonify: Un JSON que contiene el ID del nodo si es válido, de lo contrario, retorna {"id": 0}.
    """
    conexion = mysql.connector.connect(
        host="localhost",         
        user="root",              
        password="marr5604",     
        database="server_central" 
    )
    
    cursor = conexion.cursor()
    cursor.execute(f"SELECT id FROM nodos WHERE nombre_nodo_local = %s AND password = %s", (name, password))
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    if len(resultados) == 0:
        return jsonify({"id": 0})  
    return jsonify({"id": resultados[0][0]})  

def verification_client(id):
    """Verifica la existencia de un cliente por su ID.

    Args:
        id (int): ID del cliente a verificar.

    Returns:
        jsonify: Un JSON que contiene el ID del cliente si es válido, de lo contrario, retorna {"id": 0}.
    """
    conexion = mysql.connector.connect(
        host="localhost",         
        user="root",              
        password="marr5604",    
        database="server_central" 
    )
    
    cursor = conexion.cursor()
    cursor.execute(f"SELECT id FROM clientes WHERE id = %s", (id))
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    if len(resultados) == 0:
        return jsonify({"id": 0}) 
    return jsonify({"id": resultados[0][0]})  


def verification_client_PWA(name, email, phone, password):
    """Verifica las credenciales de un cliente a través de la PWA.

    Args:
        name (str): Nombre del cliente.
        email (str): Correo electrónico del cliente.
        phone (str): Número de teléfono del cliente.
        password (str): Contraseña del cliente.

    Returns:
        jsonify: Un JSON que contiene el ID del cliente si es válido, de lo contrario, retorna {"id": 0}.
    """
    conexion = mysql.connector.connect(
        host="localhost", 
        user="root", 
        password="marr5604", 
        database="server_central"  
    )

    cursor = conexion.cursor()
    query = "SELECT id FROM clientes WHERE nombre = %s AND correo = %s AND telefono = %s AND contrasena = %s"
    cursor.execute(query, (name, email, phone,password))

    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()

    if len(resultados) == 0:
        return jsonify({"id": 0})  

    return jsonify({"id": resultados[0][0]})

def get_client_balance(client_id):
    """Obtiene el saldo de un cliente.

    Args:
        client_id (int): ID del cliente cuyo saldo se desea obtener.

    Returns:
        float: El saldo del cliente, o 0 si no se encuentra el saldo.
    """
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="marr5604",
        database="server_central"
    )
    cursor = conexion.cursor()

    query = "SELECT saldo FROM monedero_electronico WHERE cliente_id = %s"
    cursor.execute(query, (client_id,))
    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    if resultado:
        return resultado[0]  
    return 0  


def recargar_monedero(cliente_id, monto):
    """Recarga el monedero de un cliente.

    Args:
        cliente_id (int): ID del cliente a recargar.
        monto (float): Monto a recargar.

    Returns:
        jsonify: Un JSON que indica si la recarga fue exitosa o si ocurrió un error.
    """
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="marr5604",
            database="server_central"
        )
        
        cursor = conexion.cursor()

        cursor.callproc('recargar_monedero', [cliente_id, float(monto)])

        conexion.commit()

        cursor.close()
        conexion.close()

        return jsonify({"success": True, "message": "Recarga realizada con éxito"})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": str(err)})
    
def register_nodo(nombre_nodo, password):
    """Registra un nuevo nodo en la base de datos.

    Args:
        nombre_nodo (str): Nombre del nodo a registrar.
        password (str): Contraseña del nodo.

    Returns:
        bool: True si el registro fue exitoso, False en caso contrario.
    """
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
    """Inserta una nueva promoción en la base de datos.

    Args:
        descripcion (str): Descripción de la promoción.
        porcentaje_descuento (float): Porcentaje de descuento de la promoción.
        nodo_id (int): ID del nodo asociado (puede ser None).
        fecha_fin (str): Fecha de finalización de la promoción.

    Returns:
        jsonify: Un JSON que indica si la inserción fue exitosa o si ocurrió un error.
    """
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="marr5604",
            database="server_central"
        )
        
        cursor = conexion.cursor()

        fecha_inicio = datetime.now()

        query = """
        INSERT INTO promociones (descripcion, porcentaje_descuento, nodo_id, fecha_inicio, fecha_fin)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        if nodo_id is None:
            cursor.execute(query, (descripcion, porcentaje_descuento, None, fecha_inicio, fecha_fin))
        else:
            cursor.execute(query, (descripcion, porcentaje_descuento, nodo_id, fecha_inicio, fecha_fin))
        
        conexion.commit()

        cursor.close()
        conexion.close()

        return jsonify({"success": True, "message": "Promoción insertada con éxito"})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": str(err)})

