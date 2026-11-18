import requests

MONEDAS = {"USD": "dolar", "EUR": "euro"}

def obtener_tipo_cambio(moneda):
    if moneda not in MONEDAS:
        raise ValueError(f"Moneda no soportada: {moneda}")
    respuesta = requests.get(
        f"https://mindicador.cl/api/{MONEDAS[moneda]}",
        timeout=10,
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    return datos["serie"][0]["valor"]

moneda = input("Moneda (USD o EUR): ").strip().upper()
try:
    valor = obtener_tipo_cambio(moneda)
    texto = input("Sueldo en pesos chilenos: ").strip()
    if not texto.isdigit():
        raise ValueError("El sueldo debe ser un número entero, sin puntos ni letras")
    sueldo = int(texto)
    if sueldo <= 0:
        raise ValueError("El sueldo debe ser mayor a 0")
    pago = round(sueldo / valor, 2)
    print(f"1 {moneda} = ${valor} CLP")
    print(f"Pago: ${sueldo} CLP = {pago} {moneda}")
except ValueError as e:
    print(e)
except requests.exceptions.RequestException:
    print("No se pudo conectar con el servicio de indicadores. Intenta más tarde.")