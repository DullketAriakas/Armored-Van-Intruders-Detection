

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


# Función que permite crear el Json de respuesta de las llamadas

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
  textoCifrado=""
  insertRow={
    "data": textoCifrado,
    "timestamp": jsonResponse['timestamp'],
    "furgon_id": jsonResponse['furgon_id']
}
  dataBase.insert(insertRow)
  status=generarAcciones(jsonResponse)
  return status
	