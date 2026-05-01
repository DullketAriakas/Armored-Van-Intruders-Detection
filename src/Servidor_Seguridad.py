import functions, json, base64
from pathlib import Path
from flask import Flask, request
from cryptography.hazmat.primitives.asymmetric import dh, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

'''
En este archivo se implementa el servidor de seguridad, que se encargará de 
recibir los datos de los sensores, almacenarlos en la base de datos y gestionar 
el proceso de handshake para establecer una clave compartida con el cliente. 
También genera un par de claves RSA para firmar su clave DH y autenticar su 
identidad ante el cliente.
'''

BASE_DIR = Path(__file__).resolve().parent
SHARED_KEY_SERVER=None

#Claves RSA del servidor (Firma)

server_rsa_private_key,server_rsa_public_key=functions.createKeys_savePublic('server',BASE_DIR)
print("------ Claves RSA creadas --------- ")

public_key_bytes_server = server_rsa_public_key.public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
print("Clave RSA pública del servidor: " + public_key_bytes_server.hex())

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
	#Usamos clave compartida generada en el handshake
	global SHARED_KEY_SERVER 
	
	if request.method == 'POST':
		content = request.get_json()
		print("\n---------------- NUEVO PAQUETE RECIBIDO ----------------")
		payload_cifrado = content.get("datos_seguros", "")
		
		# Desciframos con la clave compartida
		datos_descifrados = functions.descifrar_mensaje(payload_cifrado, SHARED_KEY_SERVER)
		
		if datos_descifrados:
			print("------ Datos descifrados correctamente --------- ")
			print(json.dumps(datos_descifrados, indent=2))
			
			# Guardamos en base de datos
			status = functions.saveData(datos_descifrados, tabla_datos)
			
			# Preparamos orden de respuesta del furgón que dependerá del estado de la alarma recibido
			# Si hay alarma, le decimos que C (Cerrar). Si todo ok, A (Abrir)
			estado_alarma = datos_descifrados.get("estado_alarma", 0)
			orden = {"Actuacion": "C" if estado_alarma > 0 else "A"}
			
			# Ciframos respuesta con la clave compartida para que el cliente pueda descifrarla y actuar en consecuencia
			orden_cifrada = functions.cifrar_mensaje(orden, SHARED_KEY_SERVER)
			
			return {"orden_cifrada": orden_cifrada}, 200
			
		else:
			print("!!! Intento de hackeo o error al descifrar !!!")
			return {"error": "No se pudo descifrar"}, 400

@app.route('/handshake', methods = ['POST'])
def publicKey():
	global SHARED_KEY_SERVER
	if request.method == 'POST':
		print("------ Iniciando Handshake Solicitado --------- ")

		# Obtención de pública del cliente estableciendo el rol
		client_rsa_public_key=functions.loadPublic('server',BASE_DIR)

		public_key_bytes_client = client_rsa_public_key.public_bytes(
			encoding=serialization.Encoding.DER,
			format=serialization.PublicFormat.SubjectPublicKeyInfo
		)
		print("Clave RSA pública del cliente: " + public_key_bytes_client.hex())
		
		print("------ Payload recibido del cliente --------- ")
		content = request.get_json()

		print(json.dumps(content, indent=2))

		client_dh = base64.b64decode(content["dh_public"])
		signature_client = base64.b64decode(content["signature"])

		# Comprobación de la firma del cliente para autenticar

		try:
			client_rsa_public_key.verify(
				signature_client,
				client_dh,
				padding.PSS(
					mgf=padding.MGF1(hashes.SHA256()),
					salt_length=padding.PSS.MAX_LENGTH
				),
				hashes.SHA256()
			)
			print("Verificación del cliente mediante firma exitosa")
		except Exception as e:
			print("No se ha podido verificar la identidad del cliente: ", e)
			return "No se reconoce el cliente", 500

		# Carga de parámetros DH
		p = content["p"]
		g = content["g"]

		params = dh.DHParameterNumbers(p, g).parameters()

		client_pub = serialization.load_der_public_key(client_dh)

		# Generar claves DH del server en base a parámetros

		server_dh_private_key = params.generate_private_key()
		server_dh_public_key = server_dh_private_key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

		print("------ Claves DH creadas --------- ")

		print("Clave DH publica: "+ server_dh_public_key.hex())

		# Firma del servidor para autenticación

		signature_server = server_rsa_private_key.sign(
			server_dh_public_key,
			padding.PSS(
				mgf=padding.MGF1(hashes.SHA256()),
				salt_length=padding.PSS.MAX_LENGTH
			),
			hashes.SHA256()
		)

		# Enviar clave DH al cliente y establecer la clave compartida
		payload= {
			"server_dh": base64.b64encode(server_dh_public_key).decode(),
			"signature": base64.b64encode(signature_server).decode()
		}

		print("Payload enviado al cliente: ")
		print(json.dumps(payload, indent=2))

		shared_key = server_dh_private_key.exchange(client_pub)

		SHARED_KEY_SERVER = HKDF(
			algorithm=hashes.SHA256(),
			length=32,
			salt=None,
			info=b"handshake"
		).derive(shared_key)

		print("------ Finalizando Handshake --------- ")
		print("SERVER SHARED KEY:", SHARED_KEY_SERVER.hex())

		return payload, 200


app.run(host="0.0.0.0", port="5001")