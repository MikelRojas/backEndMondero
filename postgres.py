from flask import jsonify
import psycopg2

#Resive credenciales de la db local t devuelve una lista de tuplas con la informacion de los productos
def get_products(host,dbname,user,password,port):
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