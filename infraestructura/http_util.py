from dominio.excepciones import EcoTechError

class ErrorServicio(EcoTechError):
    """Error de una API externa, con un mensaje seguro para el usuario."""


def revisar_respuesta(respuesta, servicio):
    codigo = respuesta.status_code
    if codigo == 200:
        return
    if codigo == 404:
        raise ErrorServicio(f"El servicio de {servicio} no encontró lo consultado.")
    if codigo in (401, 403):
        raise ErrorServicio(f"El servicio de {servicio} rechazó el acceso.")
    if codigo == 429:
        raise ErrorServicio(f"Demasiadas consultas a {servicio}. Espera unos minutos.")
    if codigo >= 500:
        raise ErrorServicio(f"El servicio de {servicio} está con fallas. Intenta más tarde.")
    raise ErrorServicio(f"El servicio de {servicio} rechazó la consulta.")