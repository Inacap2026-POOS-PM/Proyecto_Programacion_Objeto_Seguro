import requests
from infraestructura.consulta_repositorio import guardar_clima
import re

PATRON_CIUDAD = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .\-]{2,60}")

DESCRIPCIONES = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna débil", 53: "Llovizna", 55: "Llovizna intensa",
    56: "Llovizna helada", 57: "Llovizna helada intensa",
    61: "Lluvia débil", 63: "Lluvia", 65: "Lluvia intensa",
    66: "Lluvia helada", 67: "Lluvia helada intensa",
    71: "Nieve débil", 73: "Nieve", 75: "Nieve intensa", 77: "Granizo fino",
    80: "Chubascos débiles", 81: "Chubascos", 82: "Chubascos violentos",
    85: "Chubascos de nieve", 86: "Chubascos de nieve intensos",
    95: "Tormenta eléctrica", 96: "Tormenta con granizo", 99: "Tormenta con granizo fuerte",
}

def buscar_ciudad(ciudad):
    respuesta = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": ciudad, "count": 1, "language": "es"},
        timeout=10,
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    resultados = datos.get("results")
    if not resultados:
        raise ValueError(f"No se encontró la ciudad '{ciudad}'")
    lugar = resultados[0]
    return lugar["latitude"], lugar["longitude"]

def obtener_clima(ciudad):
    latitud, longitud = buscar_ciudad(ciudad)
    respuesta = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitud,
            "longitude": longitud,
            "current": "temperature_2m,relative_humidity_2m,weather_code",
        },
        timeout=10,
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    actual = datos["current"]
    return actual["temperature_2m"], actual["relative_humidity_2m"], actual["weather_code"]

def mostrar_clima():
    ciudad = input("Ingresa la ciudad: ").strip()
    if not ciudad:
        print("La ciudad no puede estar vacía.")
        return
    if not PATRON_CIUDAD.fullmatch(ciudad):
        print("Ciudad inválida: usa solo letras, espacios o guiones (2 a 60 caracteres).")
        return
    try:
        temperatura, humedad, codigo = obtener_clima(ciudad)
        print(f"Clima en {ciudad}")
        print(f"Temperatura: {temperatura} °C")
        print(f"Humedad: {humedad} %")
        print(f"Estado: {DESCRIPCIONES.get(codigo, 'Desconocido')}")
        estado = DESCRIPCIONES.get(codigo, "Desconocido")
        guardar_clima(ciudad, temperatura, humedad, estado)
    except ValueError as e:
        print(e)
    except requests.exceptions.RequestException:
        print("No se pudo conectar con el servicio de clima. Intenta más tarde.")
    except (KeyError, IndexError, TypeError):
        print("El servicio respondió con datos inesperados. Intenta más tarde.")