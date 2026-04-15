import time
import json
import requests
import base64
import functions
from Crypto.Cipher import AES

# 1. Configuracion servidor
SECRET_KEY = b'ClaveSecreta1234' # Clave de 16 bytes
URL_SERVIDOR = "http://localhost:5001/sensor_values"

# 3. Inicio simulación
print("------ Iniciando simulador de furgón blindado... --------- ")

try:
    with open('timeline_datos.json', 'r', encoding='utf-8') as f:    
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
    payload_cifrado = functions.cifrar_mensaje(doc_interno,SECRET_KEY)
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
            orden_legible = functions.descifrar_mensaje(orden_cifrada,SECRET_KEY)
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