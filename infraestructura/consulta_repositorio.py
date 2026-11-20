from datetime import datetime

from infraestructura.conexion import obtener_conexion

def guardar_clima(ciudad, temperatura, humedad, estado):
    with obtener_conexion() as conn:
        conn.execute(
            "INSERT INTO consulta_clima (ciudad, temperatura, humedad, estado, fecha) VALUES (?, ?, ?, ?, ?)",
            (ciudad, temperatura, humedad, estado, datetime.now().isoformat(timespec="seconds")),
        )

def guardar_pago(moneda, valor, sueldo, pago):
    with obtener_conexion() as conn:
        conn.execute(
            "INSERT INTO consulta_pago (moneda, valor_clp, sueldo_clp, pago, fecha) VALUES (?, ?, ?, ?, ?)",
            (moneda, valor, sueldo, pago, datetime.now().isoformat(timespec="seconds")),
        )

def ultimo_clima(ciudad):
    with obtener_conexion() as conn:
        return conn.execute(
            "SELECT temperatura, humedad, estado, fecha FROM consulta_clima "
            "WHERE lower(ciudad) = lower(?) ORDER BY id DESC LIMIT 1",
            (ciudad,),
        ).fetchone()