from flask import Flask, jsonify, request
from my_sql import insertar_promocion, sign_in_verification_nodo, verification_client_PWA, get_client_balance,recargar_monedero, register_nodo
from postgres import get_products, set_products, set_ventas
from flask_cors import CORS
from threading import Timer
  
app = Flask(__name__)
CORS(app)
# Ruta de prueba, tipo GET
@app.route('/')
def home():
    return jsonify({"message": "¡Bienvenido a la API!"})

verificacion_clientes = {}

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # Permitir todos los orígenes
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'  # Métodos permitidos
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'  # Encabezados permitidos
    return response

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')  # Si quieres manejar la contraseña, puedes agregar su lógica aquí

    # Llamar a la función de verificación
    response = verification_client_PWA(name, email, phone, password)

    # Asumiendo que la función devuelve un JSON con el id
    if response.json['id'] != 0:
        # Aquí puedes agregar lógica para obtener el saldo del cliente, por ejemplo:
        balance = get_client_balance(response.json['id'])  # Implementa esta función según tu lógica
        return jsonify({
            "id": response.json['id'],
            "name": name,
            "balance": balance
        })
    else:
        return jsonify({"id": 0}), 401  # Retorna 0 si el usuario no existe o las credenciales son incorrectas

@app.route('/insertar_promocion', methods=['POST'])
def insertar_promocion_route():
    try:
        data = request.get_json()

        # Obtener los valores del JSON enviado por el cliente
        descripcion = data.get('descripcion')
        porcentaje_descuento = data.get('porcentaje_descuento')
        nodo_id = data.get('nodo_id')  # Este campo es opcional, puede ser None
        fecha_fin = data.get('fecha_fin')  # Formato esperado: "YYYY-MM-DD HH:MM:SS"

        if not descripcion or not porcentaje_descuento or not fecha_fin:
            return jsonify({"success": False, "message": "Faltan campos obligatorios"}), 400

        # Llamar a la función que inserta la promoción en la base de datos
        resultado = insertar_promocion(descripcion, porcentaje_descuento, nodo_id, fecha_fin)
        return resultado

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def eliminar_verificacion(cliente_id):
    # Elimina el ID de cliente de la lista global después de 20 segundos
    if cliente_id in verificacion_clientes:
        del verificacion_clientes[cliente_id]

# Ruta para obtener un mensaje personalizado con parámetros
@app.route('/verificacion_nodo', methods=['GET'])
def verificar_nodo():
    nombre = request.args.get('nombre')
    password = request.args.get('password')
    
    # Llamar a la función de verificación
    return sign_in_verification_nodo(nombre, password)

@app.route('/registrar_nodo', methods=['POST'])
def registrar_nodo():
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
    id = request.args.get('id')
    monto = request.args.get('monto')
    return recargar_monedero(id, monto)

# Ruta para sumar dos números usando método POST
@app.route('/obtener_productos', methods=['POST'])
def obtener_productos():
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
    cliente_id = request.args.get('id')
    
    if cliente_id not in verificacion_clientes:
        # Agregar el ID del cliente a la lista de verificación
        verificacion_clientes[cliente_id] = False
        
        # Configurar un temporizador para eliminar la verificación después de 20 segundos
        Timer(50.0, eliminar_verificacion, args=[cliente_id]).start()

    # Espera a que llegue la respuesta del cliente
    while cliente_id in verificacion_clientes and not verificacion_clientes[cliente_id]:
        pass  # Esperar
    estado = verificacion_clientes.get(cliente_id, False)
    eliminar_verificacion(cliente_id)
    return jsonify({"estado": estado})

@app.route('/respuesta_cliente', methods=['GET'])
def respuesta_cliente():
    cliente_id = request.args.get('id')
    if cliente_id in verificacion_clientes:
        verificacion_clientes[cliente_id] = True  
        return jsonify({"estado": True})
    return jsonify({"estado": False})

if __name__ == '__main__':
    app.run(debug=True)
