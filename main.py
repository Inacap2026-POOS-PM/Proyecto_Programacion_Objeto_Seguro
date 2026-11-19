from datetime import date
import getpass
from infraestructura.repositorios import crear_repositorios
from infraestructura.conexion import ErrorDeConexion, inicializar_bd
from dominio.departamento import Departamento
from dominio.empleado import Empleado, Usuario
from dominio.excepciones import (
    EcoTechError,
    EmpleadoNoEncontradoError,
)
from dominio.persona import Persona
from dominio.registro_tiempo import RegistroTiempo
from autenticacion import iniciar_sesion
from infraestructura.usuario_repositorio import contar_cuentas, crear_cuenta
from infraestructura.servicio_clima import mostrar_clima
from infraestructura.servicio_cambio import mostrar_cambio

# ---------------------------------------------------------------
# Lectura de datos por consola (cada función repite hasta que el
# dato sea válido, así una entrada incorrecta nunca detiene el programa)
# ---------------------------------------------------------------

def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  El dato no puede estar vacío.")


def pedir_entero(mensaje):
    while True:
        try:
            return int(input(mensaje).strip())
        except ValueError:
            print("  Debes ingresar un número entero (sin puntos ni letras).")


def pedir_fecha(mensaje):
    while True:
        texto = input(mensaje).strip()
        try:
            return date.fromisoformat(texto)
        except ValueError:
            print("  Fecha inválida. Usa el formato AAAA-MM-DD, por ejemplo 2024-03-01.")


# ---------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------

def registrar_empleado(repo_empleados, repo_departamentos):
    rut = pedir_texto("RUT (ej. 12345678-9): ")
    nombre = pedir_texto("Nombre completo: ")
    fecha = pedir_fecha("Fecha de ingreso (AAAA-MM-DD): ")
    sueldo = pedir_entero("Sueldo base (entero, sin puntos): ")
    # Las reglas del negocio (RUT, nombre, sueldo) las valida la clase Empleado
    empleado = Empleado(rut, nombre, fecha, sueldo)
    repo_empleados.guardar(empleado)
    print(f"  Empleado guardado: {empleado}")


def buscar_empleado(repo_empleados, repo_departamentos):
    rut = pedir_texto("RUT a buscar: ")
    empleado = repo_empleados.obtener(rut)
    print(f"  {empleado}" if empleado else "  No existe un empleado activo con ese RUT.")


def listar_empleados(repo_empleados, repo_departamentos):
    filtro = input("Filtrar por nombre (Enter para ver todos): ").strip()
    empleados = repo_empleados.listar(nombre_contiene=filtro or None)
    if not empleados:
        print("  No hay empleados para mostrar.")
    for empleado in empleados:
        print(f"  {empleado}")


def actualizar_sueldo(repo_empleados, repo_departamentos):
    rut = pedir_texto("RUT del empleado: ")
    empleado = repo_empleados.obtener(rut)
    if empleado is None:
        raise EmpleadoNoEncontradoError("No existe un empleado activo con ese RUT")
    empleado.sueldo_base = pedir_entero("Nuevo sueldo base: ")
    repo_empleados.actualizar(empleado)
    print(f"  Sueldo actualizado: {empleado}")


def dar_de_baja(repo_empleados, repo_departamentos):
    rut = pedir_texto("RUT del empleado a dar de baja: ")
    if repo_empleados.eliminar(rut):
        print("  Empleado dado de baja.")
    else:
        print("  No existe un empleado activo con ese RUT.")


def registrar_departamento(repo_empleados, repo_departamentos):
    nombre = pedir_texto("Nombre del departamento: ")
    gerente = pedir_texto("Gerente: ")
    departamento = Departamento(None, nombre, gerente)
    repo_departamentos.guardar(departamento)
    print(f"  Departamento guardado: {departamento}")


def listar_departamentos(repo_empleados, repo_departamentos):
    departamentos = repo_departamentos.listar()
    if not departamentos:
        print("  No hay departamentos registrados.")
    for departamento in departamentos:
        print(f"  {departamento}")


# ---------------------------------------------------------------
# Pruebas automáticas (incluye el intento de inyección SQL)
# ---------------------------------------------------------------

def probar_empleados(repo):
    print("--- Empleados ---")
    # Si una corrida anterior dejó a Ana activa, se la da de baja primero para
    # que la prueba parta siempre del mismo estado y se pueda repetir.
    repo.eliminar("12345678-9")
    ana = Empleado("12345678-9", "Ana Rojas", date(2024, 3, 1), 950_000)
    repo.guardar(ana)
    print("1. Guardar y leer por RUT      :", repo.obtener("12345678-9"))
    print("2. Total de empleados activos  :", len(repo.listar()))
    print("3. Filtro 'Ana' (parametrizado):", len(repo.listar(nombre_contiene="Ana")), "resultado(s)")
    print("4. Inyeccion en el filtro      :", repo.listar(nombre_contiene="' OR '1'='1"), "(sin resultados: ataque inofensivo)")
    print("5. Inyeccion en el RUT         :", repo.obtener("' OR '1'='1"), "(no existe: ataque inofensivo)")
    ana.sueldo_base = 1_050_000
    print("6. Actualizar sueldo (filas)   :", repo.actualizar(ana))
    print("7. Dar de baja (borrado logico):", repo.eliminar("12345678-9"))
    print("8. Leer tras la baja           :", repo.obtener("12345678-9"), "(ya no aparece)")


def probar_departamentos(repo):
    print("--- Departamentos ---")
    ti = Departamento(None, "Tecnología", "Pedro Soto")
    repo.guardar(ti)
    print("1. Guardar (id asignado)       :", ti.id, ti.nombre, ti.gerente)
    print("2. Total de departamentos      :", len(repo.listar()))
    print("3. Inyeccion en el filtro      :", repo.listar(nombre_contiene="' OR '1'='1"), "(sin resultados: ataque inofensivo)")
    print("4. Inyeccion en el id          :", repo.obtener("' OR '1'='1"), "(no existe: ataque inofensivo)")
    ti.gerente = "María Pérez"
    print("5. Actualizar gerente (filas)  :", repo.actualizar(ti))
    print("6. Leer gerente actualizado    :", repo.obtener(ti.id).gerente)
    print("7. Eliminar                    :", repo.eliminar(ti.id))
    print("8. Leer tras eliminar          :", repo.obtener(ti.id), "(ya no existe)")


def ejecutar_pruebas(repo_empleados, repo_departamentos):
    for prueba, repo in ((probar_empleados, repo_empleados),
                         (probar_departamentos, repo_departamentos)):
        try:
            prueba(repo)
        except (EcoTechError, ErrorDeConexion) as e:
            print("Error:", e)


# ---------------------------------------------------------------
# Polimorfismo: un mismo mensaje (str / print) sobre objetos de
# distintas clases, sin preguntar de qué tipo es cada uno
# ---------------------------------------------------------------

def demostrar_polimorfismo(repo_empleados, repo_departamentos):
    persona = Persona("11111111-1", "Persona de ejemplo")
    empleado = Empleado("22222222-2", "Empleado de ejemplo", date(2024, 1, 15), 800_000)
    usuario = Usuario("33333333-3", "Usuario de ejemplo", date(2023, 6, 1),
                      900_000, "uejemplo", "clave-de-ejemplo", "Administrador")
    usuario.asignar_departamento(Departamento(1, "Tecnología", "Pedro Soto"))
    usuario.registrarHoras(RegistroTiempo(1, 8, date(2026, 10, 1), "Desarrollo", usuario.rut, 1))
    for objeto in (persona, empleado, usuario):
        print(f"  [{type(objeto).__name__}] {objeto}")
    print(f"  {usuario.generar_informe()}")
    print(f"  Contraseña correcta : {usuario.autenticar('clave-de-ejemplo')}")
    print(f"  Contraseña incorrecta: {usuario.autenticar('otra-clave')}")
    print(f"  Permiso 'informes'  : {usuario.permiso('informes')}")
    print(f"  Permiso 'horas'     : {usuario.permiso('horas')}")


# ---------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------
def crear_cuenta_usuario(repo_empleados, repo_departamentos):
    usuario = pedir_texto("Nombre del nuevo usuario: ").lower()
    contrasena = getpass.getpass("Contraseña (mín. 8, con letras y números): ")
    repetir = getpass.getpass("Repite la contraseña: ")
    if contrasena != repetir:
        print("  Las contraseñas no coinciden.")
        return
    if len(contrasena) < 8 or contrasena.isalpha() or contrasena.isdigit():
        print("  Contraseña débil.")
        return
    crear_cuenta(usuario, contrasena, "Empleado")
    print(f"  Cuenta creada: {usuario} (Empleado)")

OPCIONES = {
    "1": ("Registrar empleado", registrar_empleado),
    "2": ("Buscar empleado por RUT", buscar_empleado),
    "3": ("Listar empleados", listar_empleados),
    "4": ("Actualizar sueldo de un empleado", actualizar_sueldo),
    "5": ("Dar de baja a un empleado", dar_de_baja),
    "6": ("Registrar departamento", registrar_departamento),
    "7": ("Listar departamentos", listar_departamentos),
    "8": ("Ejecutar pruebas automáticas (incluye inyección SQL)", ejecutar_pruebas),
    "9": ("Demostración de polimorfismo", demostrar_polimorfismo),
    "10": ("Consultar clima de un proyecto", lambda e, d: mostrar_clima()),
    "11": ("Calcular pago en moneda extranjera", lambda e, d: mostrar_cambio()),
    "12": ("Crear cuenta de empleado", crear_cuenta_usuario),
}


def mostrar_menu():
    print("\n=== EcoTech Solutions - Gestión de empleados ===")
    for clave, (texto, _) in OPCIONES.items():
        print(f"  {clave}. {texto}")
    print("  0. Salir")


def main():
    try:
        repo_empleados, repo_departamentos = crear_repositorios()
    except ErrorDeConexion:
        print("Error de configuración: no se pudo preparar la base de datos.")
        return
    try:
        inicializar_bd()
        if contar_cuentas() == 0:
            print("No hay cuentas. Crea el administrador inicial.")
            while True:
                usuario = pedir_texto("Usuario: ").lower()
                contrasena = getpass.getpass("Contraseña (mín. 8, con letras y números): ")
                if not contrasena:
                    print("La contraseña no puede estar vacía.")
                    continue
                repetir = getpass.getpass("Repite la contraseña: ")
                if contrasena != repetir:
                    print("Las contraseñas no coinciden. Intenta de nuevo.")
                    continue
                if not usuario or len(contrasena) < 8 or contrasena.isalpha() or contrasena.isdigit():
                    print("Usuario vacío o contraseña débil. Intenta de nuevo.")
                    continue
                crear_cuenta(usuario, contrasena, "Administrador")
                break
    except ErrorDeConexion:
        print("No se pudo preparar la base de datos.")
        return

    sesion = iniciar_sesion()
    if sesion is None:
        return
    

    while True:
        mostrar_menu()
        try:
            opcion = input("Elige una opción: ").strip()
            if opcion == "0":
                print("Hasta luego.")
                return
            if opcion not in OPCIONES:
                print("  Opción no válida. Elige un número del menú.")
                continue
            if opcion in ("11", "12") and sesion[1] != "Administrador":
                print("  No tienes permiso para esta opción.")
                continue            
            OPCIONES[opcion][1](repo_empleados, repo_departamentos)
        except EcoTechError as e:
            print("  Error:", e)
        except ErrorDeConexion:
            print("  Error: no se pudo acceder a la base de datos. Intenta nuevamente.")
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada cancelada. Hasta luego.")
            return


if __name__ == "__main__":
    main()
