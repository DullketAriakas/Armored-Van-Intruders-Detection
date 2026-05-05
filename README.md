

# Sistema IoT de Monitorización y Seguridad para Furgones Blindados

Este proyecto implementa una arquitectura IoT segura para la sensorización y monitorización en tiempo real de una flota de furgones blindados. Su objetivo es detectar anomalías físicas (caídas bruscas de presión o cambios de temperatura) que puedan indicar un ataque o un intento de robo, respondiendo con órdenes de actuación (ej. bloqueo de puertas) de manera inmediata.

Destacamos de este sistema su sistema de encriptado con autenticación mutua, establecimiento seguro de claves compartidas y cifrado de telemetría, asegurando la confidencialidad, integridad y el no-repudio de las comunicaciones.

---

## Arquitectura del Sistema

El proyecto se divide en tres nodos principales:

1. **Nodo Sensor-Actuador (Cliente):** lee los datos simulados de los sensores, cifra la telemetría, la envía por HTTP y ejecuta sobre el furgón las órdenes de bloqueo recibidas.
2. **Servidor de Seguridad:** recibe, autentica y descifra los datos de los furgones, almacenándolos en una base de datos local y emitiendo órdenes de respuesta ante anomalías.
3. **Tercero de Confianza (PKI Offline):** simulado por parte de los desarrolladores previo al despliegue. Se generan y distribuyen claves públicas RSA (certificados `.pem`) en los directorios del cliente y servidor para evitar ataques *Man-in-the-Middle*.

---

## Estructura del Proyecto

* **`Servidor_Seguridad.py`**: script principal del servidor construido con Flask. Escucha las peticiones, gestiona el *handshake* criptográfico y procesa la telemetría.
* **`sensor_servo_v8.py`**: script principal del cliente (furgón). En él se ejecuta el inicio de sesión, el acuerdo de clave, la lectura del archivo JSON y el envío de telemetría de forma fluída.
* **`cryptography.py`**: en este módulo se encuentran centralizadas las funciones de cifrado y descifrado, junto con elementos de comparación de los algoritmos de cifrado de bloque (AES) y de flujo (ChaCha20), así como manejo de Base64 y *padding*.
* **`db.py`**: gestión de la base de datos SQLite. Implementa persistencia segura permitiendo concurrencia (`check_same_thread=False`).
* **`server_actions.py`**: módulo con la lógica del servidor para evaluar los datos recibidos y guardar la información descifrada en la base de datos.
* **`timeline_datos.json`**: archivo que simula una línea temporal de datos, con eventos y lecturas de los sensores del furgón, generada con IA para mayor concordancia.
* **`SystemDB.db`**: archivo base de datos SQLite donde el servidor almacena los registros de telemetría continuadamente.

---

## Flujo Criptográfico

Esquema de seguridad de extremo a extremo:

1. **Autenticación (RSA):** cliente y servidor verifican sus identidades antes de enviar ningún dato, comprobando firmas digitales mediante claves asimétricas RSA de 2048 bits.
2. **Acuerdo de Claves (Diffie-Hellman):** intercambio seguro de parámetros para establecer un secreto compartido a través de la red sin que este sea interceptable.
3. **Derivación (HKDF):** fortalecimiento de la clave DH utilizando funciones basadas en HMAC para generar una clave de sesión simétrica robusta.
4. **Cifrado de Telemetría (AES / ChaCha20):** los datos en formato JSON se cifran de forma simétrica antes de empaquetarse en Base64 para su transporte sobre HTTP. También hay integrada una lógica de comparación entre las latencias de AES (bloque) y ChaCha20 (flujo).

---

## Instrucciones de Ejecución

### 1. Requisitos previos
Es necesario tener instalado Python 3.x y las siguientes librerías de terceros. Puedes instalarlas ejecutando:

```bash
pip install flask requests cryptography pycryptodome

### 2. Despliegue del Entorno
Todos los archivos deben estar en la misma carpeta. El sistema generará automáticamente los pares de claves RSA (`.pem`) la primera vez que se ejecute si estas no se encuentran presentes en el directorio.

### 3. Orden de Ejecución
Para el correcto funcionamiento del sistema, será **imprescindible** seguir el siguiente orden (necesitaremos dos terminales abiertas):

1.  **Terminal 1 - Servidor:** ejecuta el servidor de seguridad para que esté listo para recibir conexiones.
    ```bash
    python Servidor_Seguridad.py
    ```
    *El servidor se iniciará en `http://127.0.0.1:5001` y creará la base de datos `SystemDB.db` si no existe.*

2.  **Terminal 2 - Cliente (Furgón):** ejecuta el simulador del furgón.
    ```bash
    python sensor_servo_v8.py
    ```
    *El cliente realizará el handshake, autenticará al servidor y empezará a enviar los datos del archivo `timeline_datos.json`.*

---

## Resultados Esperados

Al ejecutar el cliente, lo que debemos observar en la consola será:
* **Comparativa de rendimiento:** diferencia real en milisegundos entre el cifrado AES y ChaCha20 para cada envío.
* **Simulación del Actuador:** impresión de mensajes indicando el estado del servo (bloqueo/desbloqueo de la caja) según las órdenes de seguridad enviadas por el servidor.
* **Persistencia:** todos los datos recibidos y descifrados por el servidor se guardarán automáticamente en la tabla de la base de datos para mantener la trazabilidad.

---

## Autores

Proyecto realizado para la asignatura de **Seguridad en IoT** (Máster IoT UC3M) - Mayo 2026.
* **Carlota Colmeiro Salgado**
* **Miguel Hörmanseder Hernando**