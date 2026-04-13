import socket
import functions
import time
import numpy as np
from flask import Flask, request
from datetime import datetime
from zoneinfo import ZoneInfo


sensores_esquema=[{'name': 'id', 'type': 'INTEGER', 'restrictions': 'PRIMARY KEY'},{'name': 'temperature', 'type': 'TEXT', 'restrictions': 'NOT NULL'},{'name': 'user_id', 'type': 'TEXT'}]

"""
JSON EJEMPLO
    {
    "temperature": "",
    "latitude": "",
    "longitude": "",
    "humidity": "",
    "pressure": "",
    "timestamp": ""
    }
"""
# Función que permite crear el Json de respuesta de las llamadas
def createJsonResponse(temperatura, presion, humedad,clima,gps,movimiento,actuacion,timestamp):
    
	respuestaJson={
			"Temperatura":temperatura,
			"Presion":presion,
			"Humedad":humedad,
			"Clima":clima,
			"Ubicacion":gps['ubicacion'],
			"Mascota":gps['mascota'],
			"Latitud":gps['latitud'],
			"Longitud":gps['longitud'],
			"Movimiento":movimiento,
			"Actuacion":actuacion,
			"Timestamp":timestamp

		}
	return respuestaJson

# Funcion que permite tomar las decisiones dependiendo de los valores introducidos
def generarAcciones(temperatura,humedad,presion,gps):
  actuacion="A"
  movimiento='N'

  if(gps['ubicacion']=='adentro'):
    movimiento='I'
    if(temperatura<10 or temperatura>30):
      actuacion="C"
    elif(humedad>80):
      actuacion="C"
    elif(presion<1000):
      actuacion="C"
  elif(gps['ubicacion']=='afuera'):
    movimiento='D'

  return actuacion,movimiento

# Función que ejecuta las acciones de la llamada POST
def saveData(temperatura, presion, humedad,clima,gps):
  

  
  timestamp = int(time.time() * 1000)

  dt = datetime.fromtimestamp(timestamp / 1000, tz=ZoneInfo("Europe/Madrid"))

  hora = dt.hour

  actuacion,movimiento=generarAcciones(temperatura,humedad,presion,clima,gps)
  return actuacion,movimiento,timestamp
	

app = Flask(__name__)

@app.route('/')
def index():
	return '<h1> Coming soon... </h1>'

@app.route('/sensor_values', methods = ['GET', 'POST'])
def read_sensors():
	if request.method == 'GET':
		temperature = request.args.get('temperature', default = 0)
		pressure = request.args.get('pressure', default = 0)
		humidity = request.args.get('humidity', default = 0)
		clima = request.args.get('clima', default = 0)
		ubicacion = request.args.get('ubicacion', default = 0)
		mascota = request.args.get('mascota', default = 0)
		latitude = request.args.get('latitude', default = 0)
		longitude = request.args.get('longitude', default = 0)
		GPS={'ubicacion':ubicacion,'mascota':mascota,'latitud':latitude,'longitud':longitude}

		respuestaJson=createJsonResponse(temperature, pressure, humidity,clima,GPS,'','',int(time.time() * 1000))
		return respuestaJson, 200

	elif request.method == 'POST':
		content = request.get_json()
		print("---------------- He recibido --------------------")
		print("Valor de Temperatura mediante POST: " + str(content['temperature']) + " *C")
		print("Valor de Presion mediante POST: " + str(content['latitude']) + " hPa")
		print("Valor de Ubicacion mediante POST: " + str(content['longitude']))
		print("Valor de Mascota mediante POST: " + str(content['humidity']))
		print("Valor de Latitude mediante POST: " + str(content['pressure']))
		print("Valor de Longitude mediante POST: " + str(content['timestamp']))
		print("-------------------------------------------------")
		# Recibir GPS conectandose a la ESP32 por BT
		GPS={'ubicacion':content['ubicacion'],'mascota':content['mascota'],'latitud':content['latitude'],'longitud':content['longitude']}

		actuacion,movimiento,time=saveData(content['temperature'],content['pressure'],content['humidity'],content['clima'],GPS)
		respuestaJson=createJsonResponse(content['temperature'], content['pressure'], content['humidity'],content['clima'],GPS,movimiento,actuacion,time)

		return respuestaJson, 200



tabla_datos=functions.DataBase("SystemDB","SensoresFurgon")
tabla_datos.create_table(sensores_esquema)


app.run(host="0.0.0.0", port="5001")