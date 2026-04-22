import functions, json
from pathlib import Path
from flask import Flask, request
import base64
from cryptography.hazmat.primitives.asymmetric import dh, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

BASE_DIR = Path(__file__).resolve().parent
SHARED_KEY_SERVER=None

#Claves RSA del servidor (Firma)

server_rsa_private_key,server_rsa_public_key,client_rsa_public_key=functions.createKeys('server',BASE_DIR)


print("Claves RSA creadas")
# Generación de parámetros Diffie - Hellman (Intercambio Clave)

parameters = dh.generate_parameters(generator=2, key_size=1024)

server_dh_private_key     = parameters.generate_private_key()
server_dh_public_key      = server_dh_private_key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)


print("Claves DH creadas")

#Firmar la clave

signature = server_rsa_private_key.sign(
    server_dh_public_key,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)



#Estructura de la tabla
sensores_esquema=[{'name': 'id', 'type': 'INTEGER', 'restrictions': 'PRIMARY KEY'},
				  {'name': 'data', 'type': 'TEXT', 'restrictions': 'NOT NULL'},
				  {'name': 'timestamp', 'type': 'TEXT', 'restrictions': 'NOT NULL'},
				  {'name': 'furgon_id', 'type': 'TEXT', 'restrictions': 'NOT NULL'}]

tabla_datos=functions.DataBase("SystemDB","SensoresFurgon")
tabla_datos.create_table(sensores_esquema)

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


		status=functions.saveData(content,tabla_datos)
		respuestaJson=functions.createJsonResponse(status,content['timestamp'])

		return respuestaJson, 200

@app.route('/handshake', methods = ['GET','POST'])
def publicKey():
	global SHARED_KEY_SERVER
	if request.method == 'GET':
		payload = {
			"type": "server_hello",
			"dh_public": base64.b64encode(server_dh_public_key).decode(),
			"signature": base64.b64encode(signature).decode(),
			"p": parameters.parameter_numbers().p,
			"g": parameters.parameter_numbers().g
		}
		return payload, 200
	
	if request.method == 'POST':
		content = request.get_json()
		client_pub = serialization.load_der_public_key(
			base64.b64decode(content["client_dh"])
		)

		shared_key = server_dh_private_key.exchange(client_pub)

		SHARED_KEY_SERVER = HKDF(
			algorithm=hashes.SHA256(),
			length=32,
			salt=None,
			info=b"handshake"
		).derive(shared_key)

		print("SERVER KEY:", SHARED_KEY_SERVER.hex())

		return "ACK", 200


app.run(host="0.0.0.0", port="5001")