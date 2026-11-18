import requests

def buscar_ciudad(ciudad):
    respuesta = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": ciudad, "count": 1, "language": "es"},
        timeout=10,
    )
    datos = respuesta.json()
    lugar = datos["results"][0]
    return lugar["latitude"], lugar["longitude"]

print(buscar_ciudad("Coronel"))