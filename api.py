from flask import Flask, jsonify, request
from my_sql import insertar_promocion, sign_in_verification_nodo, verification_client_PWA, get_client_balance,recargar_monedero, register_nodo
from postgres import get_products, set_products, set_ventas
from flask_cors import CORS
from threading import Timer
  
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    """Ruta de inicio de la API.

    Returns:
        jsonify: Mensaje de bienvenida en formato JSON.
    """
    return jsonify({"message": "¡Bienvenido a la API!"})

verificacion_clientes = {}

@app.after_request
def add_cors_headers(response):
    """Agrega cabeceras CORS a todas las respuestas.

    Args:
        response: La respuesta de la solicitud.

    Returns:
        response: La respuesta con las cabeceras CORS añadidas.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'  
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'  
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'  
    return response

@app.route('/login', methods=['POST'])
def login():
    """Ruta para iniciar sesión de un cliente.

    Args:
        request: Datos JSON que incluyen 'name', 'email', 'phone', 'password'.

    Returns:
        jsonify: Información del cliente y su saldo si la autenticación es exitosa, o un error 401 si no.
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password') 

    response = verification_client_PWA(name, email, phone, password)

    if response.json['id'] != 0:
        balance = get_client_balance(response.json['id'])  
        return jsonify({
            "id": response.json['id'],
            "name": name,
            "balance": balance
        })
    else:
        return jsonify({"id": 0}), 401  

@app.route('/insertar_promocion', methods=['POST'])
def insertar_promocion_route():
    """Ruta para insertar una promoción.

    Args:
        request: Datos JSON que incluyen 'descripcion', 'porcentaje_descuento', 'nodo_id', 'fecha_fin'.

    Returns:
        jsonify: Resultado de la inserción o un error si faltan campos.
    """
    try:
        data = request.get_json()

        descripcion = data.get('descripcion')
        porcentaje_descuento = data.get('porcentaje_descuento')
        nodo_id = data.get('nodo_id')  
        fecha_fin = data.get('fecha_fin')  

        if not descripcion or not porcentaje_descuento or not fecha_fin:
            return jsonify({"success": False, "message": "Faltan campos obligatorios"}), 400

        resultado = insertar_promocion(descripcion, porcentaje_descuento, nodo_id, fecha_fin)
        return resultado

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def eliminar_verificacion(cliente_id):
    """Elimina el ID de cliente de la lista de verificación después de 20 segundos.

    Args:
        cliente_id: ID del cliente a eliminar.
    """
    if cliente_id in verificacion_clientes:
        del verificacion_clientes[cliente_id]

@app.route('/verificacion_nodo', methods=['GET'])
def verificar_nodo():
    """Ruta para verificar un nodo.

    Args:
        nombre: Nombre del nodo (query parameter).
        password: Contraseña del nodo (query parameter).

    Returns:
        Resultado de la verificación del nodo.
    """
    nombre = request.args.get('nombre')
    password = request.args.get('password')
    
    return sign_in_verification_nodo(nombre, password)

@app.route('/registrar_nodo', methods=['POST'])
def registrar_nodo():
    """Ruta para registrar un nuevo nodo.

    Args:
        request: Datos JSON que incluyen 'nombreNodo' y 'password'.

    Returns:
        jsonify: Mensaje de éxito o error al registrar el nodo.
    """
    data = request.get_json()
    nombre_nodo = data.get('nombreNodo')
    password = data.get('password')

    exito = register_nodo(nombre_nodo, password)

    if exito:
        return jsonify({"message": "Nodo registrado exitosamente"}), 201
    else:
        return jsonify({"message": "Error al registrar el nodo"}), 400

@app.route('/recargar_cliente', methods=['GET'])
def recargar_cliente():
    """Ruta para recargar el monedero de un cliente.

    Args:
        id: ID del cliente (query parameter).
        monto: Monto a recargar (query parameter).

    Returns:
        Resultado de la recarga.
    """
    id = request.args.get('id')
    monto = request.args.get('monto')
    return recargar_monedero(id, monto)

@app.route('/obtener_productos', methods=['POST'])
def obtener_productos():
    """Ruta para obtener productos.

    Args:
        request: Datos JSON con credenciales de base de datos.

    Returns:
        jsonify: Lista de productos.
    """
    data = request.get_json()
    host = data.get('host')
    dbname = data.get('dbname')
    user = data.get('user')
    password = data.get('password')
    port = data.get('port')
    valor = get_products(host, dbname, user, password, port)
    return jsonify({"data": valor})

@app.route('/insertar_producto', methods=['POST'])
def insertar_producto():
    """Ruta para insertar un nuevo producto.

    Args:
        request: Datos JSON con credenciales de base de datos y detalles del producto.

    Returns:
        jsonify: Resultado de la inserción del producto.
    """
    data = request.get_json()
    host = data.get('host')
    dbname = data.get('dbname')
    user = data.get('user')
    password = data.get('password')
    port = data.get('port')
    name = data.get('name')
    price = data.get('price')
    stok = data.get('stok')
    valor = set_products(host, dbname, user, password, port,name,price,stok)
    return jsonify({"data": valor})

@app.route('/insertar_venta', methods=['POST'])
def insertar_venta():
    """Ruta para registrar una venta.

    Args:
        request: Datos JSON con credenciales de base de datos y detalles de la venta.

    Returns:
        jsonify: Resultado de la inserción de la venta.
    """
    data = request.get_json()
    host = data.get('host')
    dbname = data.get('dbname')
    user = data.get('user')
    password = data.get('password')
    port = data.get('port')
    id_client = data.get('id_client')
    total = data.get('total')
    pay = data.get('pay')
    nodo = data.get('nodo')
    products = data.get('products')
    valor = set_ventas(host, dbname, user, password, port, id_client, total, pay, nodo, products)
    return jsonify({"data": valor})

@app.route('/verificar_cliente', methods=['GET'])
def verificar_cliente():
    """Ruta para verificar el estado de un cliente.

    Args:
        cliente_id: ID del cliente (query parameter).

    Returns:
        jsonify: Estado de verificación del cliente.
    """
    cliente_id = request.args.get('id')
    
    if cliente_id not in verificacion_clientes:
        verificacion_clientes[cliente_id] = False
        
        Timer(50.0, eliminar_verificacion, args=[cliente_id]).start()

    while cliente_id in verificacion_clientes and not verificacion_clientes[cliente_id]:
        pass  
    estado = verificacion_clientes.get(cliente_id, False)
    eliminar_verificacion(cliente_id)
    return jsonify({"estado": estado})

@app.route('/respuesta_cliente', methods=['GET'])
def respuesta_cliente():
    """Ruta para recibir la respuesta de un cliente.

    Args:
        cliente_id: ID del cliente (query parameter).

    Returns:
        jsonify: Estado de la respuesta del cliente.
    """
    cliente_id = request.args.get('id')
    if cliente_id in verificacion_clientes:
        verificacion_clientes[cliente_id] = True  
        return jsonify({"estado": True})
    return jsonify({"estado": False})

if __name__ == '__main__':
    app.run(debug=True)
