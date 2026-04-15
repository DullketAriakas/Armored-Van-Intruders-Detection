from Crypto.Cipher import AES
import base64
import json

def pad(data):
    padding_len = 16 - (len(data) % 16)
    return data + (chr(padding_len) * padding_len)

def unpad(data):
    return data[:-ord(data[-1:])]

def cifrar_mensaje(diccionario,key):
    texto_plano = json.dumps(diccionario)
    texto_padded = pad(texto_plano)
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_bytes = cipher.encrypt(texto_padded.encode('utf-8'))
    return base64.b64encode(encrypted_bytes).decode('utf-8').strip()

def descifrar_mensaje(base64_string,key):
    try:
        encrypted_bytes = base64.b64decode(base64_string)
        decipher = AES.new(key, AES.MODE_ECB)
        decrypted_padded = decipher.decrypt(encrypted_bytes).decode('utf-8')
        texto_plano = unpad(decrypted_padded)
        return json.loads(texto_plano)
    except Exception as e:
        print(">>> Fallo de seguridad al descifrar:", e)
        return None