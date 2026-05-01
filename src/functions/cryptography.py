from Crypto.Cipher import AES, ChaCha20
import base64
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os, subprocess

def pad(data):
    padding_len = 16 - (len(data) % 16)
    return data + (chr(padding_len) * padding_len)

def unpad(data):
    return data[:-ord(data[-1:])]


def cifrar_mensaje(diccionario,key):
    texto_plano = json.dumps(diccionario) # cogemos diccionario json
    texto_padded = pad(texto_plano) # rellenamos el texto para que sea múltiplo de 16 bytes
    cipher = AES.new(key, AES.MODE_ECB) # lo ciframos con AES en modo ECB con la clave acordada
    encrypted_bytes = cipher.encrypt(texto_padded.encode('utf-8'))
    return base64.b64encode(encrypted_bytes).decode('utf-8').strip() # lo devolvemos al formato base64 para que se pueda enviar por la red sin problemas de codificación

def descifrar_mensaje(base64_string,key):
    try:
        encrypted_bytes = base64.b64decode(base64_string)
        decipher = AES.new(key, AES.MODE_ECB)
        decrypted_padded = decipher.decrypt(encrypted_bytes).decode('utf-8')
        texto_plano = unpad(decrypted_padded)
        return json.loads(texto_plano)
    except Exception as e:
        print(">>>>> Fallo de seguridad al descifrar:", e)
        return None

# Funciones para generar claves RSA, guardar la clave pública y cargar la clave pública del otro
def loadPublic(role,root):
    key_dir = root / "keys" # el directorio donde se guardan las claves públicas, se asume que ya se han generado con createKeys_savePublic
    if role=='server':
        with open(key_dir / "client_public.pem", "rb") as f:
            return serialization.load_pem_public_key(f.read())

    elif role=='client':
        with open(key_dir / "server_public.pem", "rb") as f:
            return serialization.load_pem_public_key(f.read())
    

# Función para generar un par de claves RSA, guardar la clave pública y devolver ambas claves
def createKeys_savePublic(role, root):
    key_dir = root / "keys"
    os.makedirs(key_dir, exist_ok=True)
    if role=='server':
        public_path  = key_dir / "server_public.pem"

    elif role=='client':
        public_path  = key_dir / "client_public.pem"

    own_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    own_public  = own_private.public_key()

    with open(public_path, "wb") as f:
        f.write(own_public.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
    
    return own_private, own_public

# Mismas funciones de cifrado pero con ChaCha20, que es un cifrado de flujo más moderno y seguro que AES, aunque no es tan común en IoT. 
# Se incluye para mostrar una alternativa más robusta al AES en modo ECB, que es inseguro. 
# ChaCha20 maneja el relleno y el nonce de forma diferente, por lo que no necesita padding ni un modo de operación específico.

def cifrar_mensaje_chacha20(diccionario, key):
    texto_plano = json.dumps(diccionario).encode('utf-8')
    # Creamos el candado ChaCha20 con nuestra clave compartida
    cipher = ChaCha20.new(key=key) 
    ciphertext = cipher.encrypt(texto_plano)
    
    # ChaCha20 genera un "nonce" (num aleatorio único de 8 bytes). 
    # Lo necesitamos para descifrar, así que lo pegamos al principio del mensaje.
    mensaje_completo = cipher.nonce + ciphertext
    return base64.b64encode(mensaje_completo).decode('utf-8').strip()

def descifrar_mensaje_chacha20(base64_string, key):
    try:
        decoded = base64.b64decode(base64_string)
        # Separamos el nonce (primeros 8 bytes) del mensaje real
        nonce = decoded[:8]
        ciphertext = decoded[8:]
        
        cipher = ChaCha20.new(key=key, nonce=nonce)
        texto_plano = cipher.decrypt(ciphertext).decode('utf-8')
        return json.loads(texto_plano)
    except Exception as e:
        print(">>>>> Fallo ChaCha20:", e)
        return None