from infraestructura.conexion import obtener_conexion
from dominio.seguridad import crear_hash

def crear_cuenta(usuario, contrasena, rol):
    sal, hash_ = crear_hash(contrasena)
    with obtener_conexion() as conn:
        conn.execute(
            "INSERT INTO cuenta_usuario (usuario, rol, sal, hash_contrasena) VALUES (?, ?, ?, ?)",
            (usuario, rol, sal.hex(), hash_.hex()),
        )

def obtener_cuenta(usuario):
    with obtener_conexion() as conn:
        fila = conn.execute(
            "SELECT usuario, rol, sal, hash_contrasena FROM cuenta_usuario WHERE usuario = ?",
            (usuario,),
        ).fetchone()
    if fila is None:
        return None
    return fila[0], fila[1], bytes.fromhex(fila[2]), bytes.fromhex(fila[3])

def contar_cuentas():
    with obtener_conexion() as conn:
        return conn.execute("SELECT COUNT(*) FROM cuenta_usuario").fetchone()[0]