from datetime import datetime
from zoneinfo import ZoneInfo
import time

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
	