import requests

DESCRIPCIONES = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Niebla", 61: "Lluvia débil", 63: "Lluvia",
    65: "Lluvia intensa", 80: "Chubascos", 95: "Tormenta eléctrica",
}

def buscar_ciudad(ciudad):
    respuesta = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": ciudad, "count": 1, "language": "es"},
        timeout=10,
    )
    datos = respuesta.json()
    lugar = datos["results"][0]
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
    datos = respuesta.json()
    actual = datos["current"]
    return actual["temperature_2m"], actual["relative_humidity_2m"], actual["weather_code"]

ciudad = "Coronel"
temperatura, humedad, codigo = obtener_clima(ciudad)
print(f"Clima en {ciudad}")
print(f"Temperatura: {temperatura} °C")
print(f"Humedad: {humedad} %")
print(f"Estado: {DESCRIPCIONES.get(codigo, 'Desconocido')}")