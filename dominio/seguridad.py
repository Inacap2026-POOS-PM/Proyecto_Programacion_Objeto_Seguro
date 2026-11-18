import hashlib
import hmac
import os

ITERACIONES = 200_000

def crear_hash(contrasena):
    sal = os.urandom(16)
    hash_ = hashlib.pbkdf2_hmac("sha256", contrasena.encode(), sal, ITERACIONES)
    return sal, hash_

def verificar(contrasena, sal, hash_guardado):
    nuevo = hashlib.pbkdf2_hmac("sha256", contrasena.encode(), sal, ITERACIONES)
    return hmac.compare_digest(nuevo, hash_guardado)

if __name__ == "__main__":
    sal, h = crear_hash("Clave1234")
    print(h.hex())
    print(verificar("Clave1234", sal, h))
    print(verificar("otra", sal, h))