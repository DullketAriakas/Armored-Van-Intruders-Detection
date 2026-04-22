from Crypto.Cipher import AES
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


def _load_public(path, peer_name):
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró la clave pública del {peer_name}. "
            f"Asegúrate de que el {peer_name} haya arrancado."
        )
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def createKeys(role,root):

    key_dir = root / "keys"

    if role=='server':
        private_path = key_dir / "server_private.pem"
        public_path  = key_dir / "server_public.pem"

    elif role=='client':
        private_path = key_dir / "client_private.pem"
        public_path  = key_dir / "client_public.pem"

    if not private_path.exists() or not public_path.exists():
        own_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        own_public  = own_private.public_key()

        with open(private_path, "wb") as f:
            f.write(own_private.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        with open(public_path, "wb") as f:
            f.write(own_public.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        subprocess.run(["icacls", str(private_path), "/inheritance:r", "/grant:r", f"{os.getlogin()}:R"], check=True)
    else:
        with open(private_path, "rb") as f:
            own_private = serialization.load_pem_private_key(f.read(), password=None)
        with open(public_path, "rb") as f:
            own_public = serialization.load_pem_public_key(f.read())

    if role=='server':

        peer_public = _load_public(key_dir / "client_public.pem", "cliente")

    elif role=='client':

        peer_public = _load_public(key_dir / "server_public.pem", "servidor")
    return own_private, own_public, peer_public

