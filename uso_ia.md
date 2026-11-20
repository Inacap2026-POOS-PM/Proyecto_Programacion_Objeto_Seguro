# Uso de IA en la ES3

Para esta evaluación usé Claude (Anthropic) como guía mientras escribía y probaba el código paso a paso. No copié todo de una vez: fui agregando cada parte, la probé y la subí como un commit separado. Estos son los casos en que tuve que corregir o mejorar lo que la IA me propuso.

## 1. El estado del clima salía como número
La primera versión mostraba el `weather_code` de Open-Meteo, y salía "3", que no le dice nada a un usuario. Agregué un diccionario para traducir los códigos a texto. Después, al consultar Concepción, me salió "Desconocido", así que completé el diccionario con todos los códigos de la documentación.

## 2. El exit() cerraba el programa completo
Cuando la ciudad venía vacía, el código usaba `exit()`. Funcionaba mientras el archivo corría solo, pero al integrarlo al menú de `main.py` cerraba todo el programa. Lo cambié por `return` para volver al menú.

## 3. Una sola fuente para el tipo de cambio
Al principio solo consultaba mindicador.cl. Durante las pruebas, la API respondió error 500 y no podía calcular ningún pago. Lo comprobé abriendo la URL en el navegador y agregué open.er-api.com como fuente de respaldo.

## 4. Respuestas inesperadas de las APIs
Al revisar el código detecté que, si una API respondía un JSON sin los campos esperados, el programa se caía con `KeyError`, porque `raise_for_status()` solo detecta errores HTTP. Agregué un `except (KeyError, IndexError, TypeError)` con un mensaje genérico.

## 5. Los errores de base de datos mostraban detalles internos
Los mensajes de error mostraban el texto de SQLite, con nombres de tablas y columnas. Lo cambié por un mensaje genérico para no exponer información del sistema.

## 6. La creación del administrador
Al principio la contraseña se pedía una sola vez. Como getpass no muestra lo que escribes, me pasó que no supe qué contraseña había puesto. Además, si me equivocaba, el programa se cerraba, y si el Enter se apretaba dos veces el usuario quedaba vacío. Lo cambié para que pida la contraseña dos veces, no acepte campos vacíos, exija letras y números, y vuelva a preguntar hasta que todo esté correcto.

## 7. Roles sin uso
El login devolvía el rol del usuario, pero no se usaba para nada. Agregué una opción para que el administrador cree cuentas de empleado, y permisos para que solo el administrador pueda calcular pagos y crear cuentas.

## 8. Códigos HTTP sin diferenciar
`raise_for_status()` trataba igual un 404, un 429 o un 500. Creé `revisar_respuesta()` en `http_util.py`, que da un mensaje distinto para cada tipo de error, y el respaldo del tipo de cambio sigue funcionando cuando mindicador responde 500.

## 9. Mejoras para robustecer la solución
Al comparar mi código con la rúbrica, hice tres mejoras:
- **Validación de los datos de la API:** antes usaba la temperatura y la humedad sin revisarlas. Ahora compruebo que sean números y que estén en rangos posibles (temperatura entre -90 y 60 °C, humedad entre 0 y 100 %).
- **Continuidad si la API falla:** si el servicio de clima no responde, el programa muestra el último dato guardado de esa ciudad, con su fecha.
- **Excepciones propias:** reemplacé `ValueError` por `DatoInvalidoError`, y `ErrorServicio` ahora hereda de `EcoTechError`. Así todos los errores del sistema quedan en una misma jerarquía.

## Conclusión
La IA me ayudó a avanzar rápido, pero varias propuestas fallaron al probarlas o tenían problemas de seguridad. Por eso probé cada cambio antes de hacer el commit y corregí lo que no funcionaba.

## Prompts usados (redactados a partir de lo que pedí)
- "¿Me ayudas con la evaluación de la Unidad 3? Es la continuación del proyecto de la Unidad 2."
- "¿No sería mejor que también se vea el nombre de la ciudad junto al consultar el clima?"
- "¿No debería la ciudad ingresarla el usuario, en vez de estar fija en el código?"
- "No me gusta que si el usuario o la contraseña quedan vacíos te deje avanzar, hagamos que te devuelva de inmediato a rellenar el campo"
- "¿No deberíamos tener una forma de crear cuentas para usuarios comunes?"
- "¿Puedes revisar a fondo el ZIP del proyecto para ver si pasé algo por alto?"