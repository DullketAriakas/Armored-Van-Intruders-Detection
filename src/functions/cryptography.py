from Crypto.Cipher import AES
import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

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

# Función que permite crear el archivo de certificación
def createKeys(rol, root):
    
    key_dir = root / "keys"

    if rol == "server":

        private_path = key_dir / "server_private.pem"
        public_path = key_dir / "server_public.pem"

        # crear si no existe
        if not private_path.exists() or not public_path.exists():

            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()


            with open(private_path, "wb") as f:
                f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                )

            with open(public_path, "wb") as f:
                f.write(
                    public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                )

            return private_key, public_key

        with open(private_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

        with open(public_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        return private_key, public_key


    elif rol == "client":

        public_path = key_dir / "server_public.pem"

        if not public_path.exists():
            raise FileNotFoundError(
                "No se encontró la clave pública del servidor. "
            )

        with open(public_path, "rb") as f:
            server_public_key = serialization.load_pem_public_key(f.read())

        return None, server_public_key

    else:
        raise ValueError("rol debe ser 'server' o 'client'")