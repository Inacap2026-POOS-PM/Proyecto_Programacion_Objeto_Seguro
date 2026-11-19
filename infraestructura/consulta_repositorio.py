from datetime import datetime

from infraestructura.conexion import obtener_conexion

def guardar_clima(ciudad, temperatura, humedad, estado):
    with obtener_conexion() as conn:
        conn.execute(
            "INSERT INTO consulta_clima (ciudad, temperatura, humedad, estado, fecha) VALUES (?, ?, ?, ?, ?)",
            (ciudad, temperatura, humedad, estado, datetime.now().isoformat(timespec="seconds")),
        )