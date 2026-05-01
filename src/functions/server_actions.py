
import json

"""
JSON EJEMPLO
doc_interno = {
        "furgon_id": "VAN_01",
        "temperature": temperature,
        "pressure": pressure,
        "latitude": latitude,
        "longitude": longitude,
        "estado_alarma": estado_alarma
    }
"""


# Función que permite crear el JSON de respuesta de las llamadas

def createJsonResponse(status,timestamp):
    
	respuestaJson={
			"status": status,
			"timestamp":timestamp

		}
	return respuestaJson

# Funcion que permite tomar las decisiones dependiendo de los valores introducidos
def generarAcciones(jsonResponse):
  status="OK"

  return status

# Función que ejecuta las acciones de la llamada POST
def saveData(jsonResponse, dataBase):
  # Convertimos el diccionario a un texto entendible para guardarlo
  textoDescifrado = json.dumps(jsonResponse) 
  
  insertRow={
    "data": textoDescifrado, # guardamos el dato real, aunque se podría guardar el JSON cifrado si se quisiera, dependiendo de las necesidades de seguridad y rendimiento
    "timestamp": jsonResponse['timestamp'],
    "furgon_id": jsonResponse['furgon_id']
  }
  
  dataBase.insert(insertRow)
  status=generarAcciones(jsonResponse)
  return status