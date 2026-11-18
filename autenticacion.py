import getpass

from dominio.seguridad import verificar, crear_hash
from infraestructura.usuario_repositorio import obtener_cuenta

MAX_INTENTOS = 3

def iniciar_sesion():
    for _ in range(MAX_INTENTOS):
        usuario = input("Usuario: ").strip().lower()
        contrasena = getpass.getpass("Contraseña: ")
        if not usuario or not contrasena:
            print("Debes ingresar usuario y contraseña.")
            continue
        cuenta = obtener_cuenta(usuario)
        if cuenta and verificar(contrasena, cuenta[2], cuenta[3]):
            print(f"Bienvenido, {cuenta[0]} ({cuenta[1]}).")
            return cuenta[0], cuenta[1]
        if cuenta is None:
            crear_hash(contrasena)
        print("Usuario o contraseña incorrectos.")
    print("Demasiados intentos fallidos.")
    return None