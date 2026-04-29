import time, sys
import json
import requests
import functions
import base64
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import dh, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# 1. Configuracion servidor
URL_SERVIDOR = "http://127.0.0.1:5001/sensor_values"
URL_BASE_SERVIDOR= "http://127.0.0.1:5001"
BASE_DIR = Path(__file__).resolve().parent

# Clave RSA pública del servidor (Firma)
client_rsa_private_key,client_rsa_public_key=functions.createKeys_savePublic('client',BASE_DIR)
server_rsa_public_key=functions.loadPublic('client',BASE_DIR)

# Generación de parámetros Diffie - Hellman (Intercambio Clave)

parameters = dh.generate_parameters(generator=2, key_size=1024)

client_dh_private_key     = parameters.generate_private_key()
client_dh_public_key      = client_dh_private_key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)


print("Claves DH creadas")


# Handshake
signature = client_rsa_private_key.sign(
    client_dh_public_key,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

payload = {
			"dh_public": base64.b64encode(client_dh_public_key).decode(),
			"signature": base64.b64encode(signature).decode(),
			"p": parameters.parameter_numbers().p,
			"g": parameters.parameter_numbers().g
		}
response_handshake = requests.post(URL_BASE_SERVIDOR+"/handshake", json=payload)


response_json=response_handshake.json()
print(response_json)
server_dh = base64.b64decode(response_json["server_dh"])
signature = base64.b64decode(response_json["signature"])

try:
    server_rsa_public_key.verify(
        signature,
        server_dh,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Verificación del servidor exitosa")
except Exception as e:
    print("No se ha podido verificar la identidad del servidor: ", e)
    sys.exit()

server_pub = serialization.load_der_public_key(server_dh)

shared_key = client_dh_private_key.exchange(server_pub)

SHARED_KEY_CLIENT = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"handshake"
).derive(shared_key)

print("CLIENT KEY:", SHARED_KEY_CLIENT.hex())

# 3. Inicio simulación
print("------ Iniciando simulador de furgón blindado... --------- ")

try:
    
    with open('src/timeline_datos.json', 'r', encoding='utf-8') as f:    
        datos_timeline = json.load(f)
    print(f"Se han cargado {len(datos_timeline)} eventos del archivo JSON")
except Exception as e:
    print("Error al leer el archivo JSON:", e)
    datos_timeline = []

# 4. Bucle principal integrando los datos
for evento in datos_timeline:
    timestamp = evento.get("timestamp", "")
    fase = evento.get("fase", "")
    temperature = evento.get("temperatura_c", 0)
    pressure = evento.get("presion_hpa", 0)
    latitude = evento.get("latitud", 0)
    longitude = evento.get("longitud", 0)
    estado_alarma = evento.get("estado_alarma", 0)
    
    print("\n" + "="*50)
    print(f"Hora: {timestamp} | {fase}")
    print(f"Sensores -> Temp: {temperature}ºC | Presión: {pressure}hPa")
    
    if estado_alarma > 0:
        print(f"----- ALARMA {estado_alarma} DETECTADA -----")

    # Preparar el JSON interno
    doc_interno = {
        "furgon_id": "VAN_01",
        "temperature": temperature,
        "pressure": pressure,
        "latitude": latitude,
        "longitude": longitude,
        "estado_alarma": estado_alarma
    }
    
    # Cifrar el paquete
    payload_cifrado = functions.cifrar_mensaje(doc_interno,SHARED_KEY_CLIENT)
    paquete_http = {"datos_seguros": payload_cifrado}
    
    print(f"Enviando JSON cifrado: {payload_cifrado[:40]}...")
    
    # Enviar POST al servidor
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(URL_SERVIDOR, json=paquete_http, headers=headers)
        
        # Recibir y descifrar respuesta
        docget = response.json()
        orden_cifrada = docget.get("orden_cifrada", "")
        
        if orden_cifrada:
            orden_legible = functions.descifrar_mensaje(orden_cifrada,SHARED_KEY_CLIENT)
            if orden_legible:
                Actuacion = orden_legible.get("Actuacion", "C")
                
                if Actuacion == "A":
                    print(">>> SIMULADOR SERVO: Movimiento a 0º (Caja Abierta)")
                    time.sleep(3)
                    print(">>> SIMULADOR SERVO: Movimiento a 90º (Caja Bloqueada)")
                else:
                    print(">>> SIMULADOR: Comando de mantener cerrado.")
        
    except Exception as e:
        print("Error en conexión HTTP. Revisar servidor", e)

    # Pausa antes del siguiente evento
    time.sleep(1)

print("\n" + "="*50)
print("------------------")
print("| FIN SIMULACIÓN |")
print("------------------")