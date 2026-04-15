import functions
from flask import Flask, request
from cryptography.hazmat.primitives.asymmetric import dh, rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


#Claves RSA del servidor (Firma)

server_rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

server_rsa_public_key = server_rsa_private_key.public_key()

print("Claves RSA creadas")
# Generación de parámetros Diffie - Hellman (Autenticación)

parameters = dh.generate_parameters(generator=2, key_size=2048)

server_dh_private_key     = parameters.generate_private_key()
server_dh_public_key      = server_dh_private_key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)


print("Claves DH creadas")
#Estructura de la tabla
sensores_esquema=[{'name': 'id', 'type': 'INTEGER', 'restrictions': 'PRIMARY KEY'},{'name': 'DATA', 'type': 'TEXT', 'restrictions': 'NOT NULL'},{'name': 'timestamp', 'type': 'TEXT', 'restrictions': 'NOT NULL'}]



app = Flask(__name__)

@app.route('/')
def index():
	return '<h1> Coming soon... </h1>'

@app.route('/sensor_values', methods = [ 'POST'])
def read_sensors():
	if request.method == 'POST':
		content = request.get_json()
		print("---------------- He recibido --------------------")
		print(str(content))
		print("-------------------------------------------------")
		# Recibir GPS conectandose a la ESP32 por BT
		GPS={'ubicacion':content['ubicacion'],'mascota':content['mascota'],'latitud':content['latitude'],'longitud':content['longitude']}

		actuacion,movimiento,time=functions.saveData(content['temperature'],content['pressure'],content['humidity'],content['clima'],GPS)
		respuestaJson=functions.createJsonResponse(content['temperature'], content['pressure'], content['humidity'],content['clima'],GPS,movimiento,actuacion,time)

		return respuestaJson, 200

@app.route('/hadshake', methods = ['GET'])
def publicKey():
    return 1



tabla_datos=functions.DataBase("SystemDB","SensoresFurgon")
tabla_datos.create_table(sensores_esquema)


app.run(host="0.0.0.0", port="5001")