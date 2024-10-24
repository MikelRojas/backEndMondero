from flask import jsonify
import psycopg2

def get_products(host,dbname,user,password,port):
    """Obtiene la lista de productos de la base de datos.

    Args:
        host (str): Dirección del servidor de la base de datos.
        dbname (str): Nombre de la base de datos.
        user (str): Nombre de usuario para acceder a la base de datos.
        password (str): Contraseña del usuario.
        port (int): Puerto de conexión a la base de datos.

    Returns:
        list: Lista de tuplas con la información de los productos.

    Raises:
        Exception: Si ocurre un error al conectar o ejecutar la consulta.
    """
    try:
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port
        )

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        results = cursor.fetchall()
        return(results)

    except Exception as e:
        print(f"Error al conectar: {e}")
        
    finally:
        if conn:
            conn.close()
            print("Conexión cerrada.")

def set_products(host, dbname, user, password, port, name, price, stock):
    """Inserta un nuevo producto en la base de datos.

    Args:
        host (str): Dirección del servidor de la base de datos.
        dbname (str): Nombre de la base de datos.
        user (str): Nombre de usuario para acceder a la base de datos.
        password (str): Contraseña del usuario.
        port (int): Puerto de conexión a la base de datos.
        name (str): Nombre del producto.
        price (float): Precio del producto.
        stock (int): Cantidad disponible del producto.

    Returns:
        str: Mensaje de éxito o error.

    Raises:
        Exception: Si ocurre un error al conectar o ejecutar la inserción.
    """
    try:
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port
        )

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, precio, stok) VALUES (%s, %s, %s)",
            (name, price, stock)
        )
        conn.commit()
        
        return "Producto agregado con éxito."

    except Exception as e:
        return f"Error al conectar: {e}"

    finally:
        if conn:
            conn.close()
            print("Conexión cerrada.")

def set_ventas(host, dbname, user, password, port, id_client, total, pay, nodo, products):
    """Registra una nueva venta en la base de datos.

    Args:
        host (str): Dirección del servidor de la base de datos.
        dbname (str): Nombre de la base de datos.
        user (str): Nombre de usuario para acceder a la base de datos.
        password (str): Contraseña del usuario.
        port (int): Puerto de conexión a la base de datos.
        id_client (int): ID del cliente que realiza la compra.
        total (float): Monto total de la venta.
        pay (float): Monto pagado por el cliente.
        nodo (str): Nodo donde se registra la venta.
        products (list): Lista de productos involucrados en la venta.

    Returns:
        str: Mensaje de éxito o error.

    Raises:
        Exception: Si ocurre un error al conectar o ejecutar las inserciones.
    """
    try:
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port
        )

        cursor = conn.cursor()
        cursor.execute(
            f"""SELECT insertar_en_ventas_local(
                {id_client},            
                {total},      
                {pay},       
                {nodo},           
                TRUE          
            )
            """
        )
        print(products)
        for x in products:
            cursor.execute(
            f"""SELECT insertar_producto_ventas(
            {x[0]},            
            {x[2]}        
            )
            """
            )
            cursor.execute(f"SELECT reducir_stok({x[0]}, {x[2]});")
        conn.commit()
        
        return "Venta exitosa"

    except Exception as e:
        return f"Error al conectar: {e}"

    finally:
        if conn:
            conn.close()
            print("Conexión cerrada.")