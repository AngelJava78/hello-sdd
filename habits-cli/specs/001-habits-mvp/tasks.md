# Tareas de implementación: MVP de habits-cli

Las tareas siguen sus dependencias; cada tarea de implementación está
dimensionada para completarse en aproximadamente 20–30 minutos como máximo.
Las tareas T1–T14 corresponden al MVP original ya implementado. T15 en adelante
desglosan el cambio posterior RF-12 y las dudas pendientes; no iniciar una tarea
hasta que sus dependencias estén completas.

1. [x] **Preparar paquete y punto de entrada mínimo** — Crear la estructura base del paquete y una entrada que permita invocar la CLI sin comandos funcionales todavía. **RF:** transversal.
   **Hecho cuando:** `python -m habits --help` inicia y muestra ayuda en español.

2. [x] **Definir lectura y escritura JSON** — Implementar almacenamiento de una colección vacía y del modelo `habits` con `name` y `completed_dates`; usar la ruta y el esquema del plan. **Depende de:** 1. **RF:** RF-9.
   **Hecho cuando:** una prueba en directorio temporal guarda JSON legible, lo vuelve a leer sin pérdida y un archivo ausente produce colección vacía.

3. [x] **Proteger datos ante JSON inválido** — Detectar JSON inválido y abortar sin sobrescribirlo. **Depende de:** 2. **RF:** RF-11.
   **Hecho cuando:** una prueba verifica código de error, mensaje claro y contenido idéntico del archivo corrupto tras la operación.

4. [x] **Implementar normalización y validación de nombres** — Rechazar vacío/solo espacios y comparar duplicados ignorando mayúsculas y espacios periféricos, preservando el nombre registrado para mostrarlo. **Depende de:** 1. **RF:** RF-2, RF-3.
   **Hecho cuando:** pruebas cubren nombre válido, nombre vacío, duplicado por mayúsculas y duplicado por espacios periféricos.

5. [x] **Implementar creación de hábitos en el núcleo** — Crear hábitos nuevos sin marcas, coordinando la validación y la escritura. **Depende de:** 2, 4. **RF:** RF-1, RF-3, RF-9.
   **Hecho cuando:** una prueba crea un hábito único y lo encuentra tras recargar los datos; un intento inválido no altera el archivo.

6. [x] **Añadir comando `add`** — Conectar `add <nombre>` con el núcleo y presentar confirmación o error en español con los códigos definidos. **Depende de:** 5. **RF:** RF-1, RF-2, RF-3.
   **Hecho cuando:** pruebas de CLI confirman código 0 para creación y código 1 para duplicado y nombre vacío, sin mutación en errores.

7. [x] **Implementar marcado diario idempotente en el núcleo** — Buscar hábitos por nombre normalizado y agregar la fecha local actual una sola vez. **Depende de:** 2, 4. **RF:** RF-4, RF-5, RF-6, RF-9.
   **Hecho cuando:** pruebas con fecha controlada verifican primer registro, repetición sin fecha duplicada y error para hábito inexistente.

8. [x] **Añadir comando `done`** — Conectar `done <nombre>` con el núcleo y traducir resultado a mensajes/códigos del contrato. **Depende de:** 7. **RF:** RF-4, RF-5, RF-6.
   **Hecho cuando:** pruebas de CLI verifican confirmación (0), ya marcado (0), inexistente con sugerencia a `list` (1) y conservación de los datos.

9. [x] **Implementar cálculo puro de racha** — Calcular días consecutivos desde hoy o ayer, o cero si la secuencia no está vigente. **Depende de:** 1. **RF:** RF-10.
   **Hecho cuando:** pruebas con hoy inyectado cubren marca hoy, ayer, secuencia consecutiva, hueco, fecha antigua, ninguna marca y cruce de mes/año.

10. [x] **Implementar consulta ordenada de hábitos** — Combinar hábitos, rachas y orden descendente por racha con desempate alfabético por nombre normalizado. **Depende de:** 2, 4, 9. **RF:** RF-7, RF-10.
    **Hecho cuando:** una prueba con varias rachas y empate verifica exactamente valores y orden, sin depender del reloj real.

11. [x] **Añadir comando `list` y estado vacío** — Mostrar nombre y racha por hábito, y el mensaje invitacional si no hay hábitos. **Depende de:** 10. **RF:** RF-7, RF-8, RF-10.
    **Hecho cuando:** pruebas de CLI validan salida y código 0 tanto para lista ordenada como para colección vacía.

12. [x] **Cubrir errores de persistencia y de invocación** — Asegurar errores de lectura/escritura en español, código 1, y argumentos/comandos inválidos con ayuda y código 2. **Depende de:** 3, 6, 8, 11. **RF:** RF-9, RF-11.
    **Hecho cuando:** pruebas verifican los códigos, mensajes, ausencia de éxito falso y conservación del archivo original cuando una escritura falla antes del reemplazo.

13. [x] **Probar el flujo completo y todos los RF** — Ejecutar `add → done → list` en almacenamiento temporal y completar la matriz de cobertura funcional. **Depende de:** 6, 8, 11, 12. **RF:** RF-1–RF-11.
    **Hecho cuando:** cada RF tiene al menos una prueba automática y la demo de extremo a extremo pasa.

14. [x] **Ejecutar la suite de aceptación** — Ejecutar la suite completa y confirmar que el comportamiento se mantiene multiplataforma, sin red y dentro del objetivo de respuesta de la spec. **Depende de:** 13. **RF:** RF-1–RF-11.
    **Hecho cuando:** `pytest -q` termina en verde y la demo manual `add → done → list` finaliza sin errores.

15. [x] **Definir el tratamiento de datos heredados** — Resolver en la spec qué ocurre con `.habits-cli.json` ya existente en `Path.home()` y con archivos presentes tanto allí como en el directorio de trabajo. No migrar ni combinar datos hasta que la regla esté aprobada. **Depende de:** ninguna. **RF:** RF-12.
    **Hecho cuando:** la spec indica explícitamente si el archivo antiguo se ignora, migra o combina, y qué sucede si ambas ubicaciones contienen datos distintos.

16. [x] **Precisar el error por falta de acceso al directorio** — Cerrar en la spec la respuesta observable cuando el directorio de trabajo no permite leer o guardar el JSON; mantener prohibido el fallback a `Path.home()`. **Depende de:** ninguna. **RF:** RF-9, RF-12.
    **Hecho cuando:** la spec define el mensaje en español, el código de salida y que no se declara éxito si la operación falla.

17. [x] **Escribir pruebas de aislamiento por directorio de trabajo** — Añadir pruebas primero para ejecutar/llamar la aplicación desde dos directorios temporales y comprobar que cada uno resuelve su propio `.habits-cli.json`, sin leer ni escribir en home. **Depende de:** 15. **RF:** RF-9, RF-12.
    **Hecho cuando:** las pruebas fallan con la ruta actual basada en home y verifican archivos independientes en ambos directorios tras implementarse el cambio.

18. [x] **Escribir pruebas para errores de acceso** — Cubrir fallo al leer y al reemplazar/escribir el archivo del directorio de trabajo, verificando el contrato acordado y que no hay fallback a home. **Depende de:** 16. **RF:** RF-9, RF-11, RF-12.
    **Hecho cuando:** las pruebas verifican el mensaje/código acordados, que no se imprime una confirmación de éxito y que el archivo preexistente permanece intacto ante fallo de reemplazo.

19. [x] **Resolver dinámicamente la ruta de almacenamiento** — Cambiar el destino predeterminado a `.habits-cli.json` en el directorio de trabajo efectivo de cada invocación; evitar fijar la ruta del proceso al importar módulos o usar `Path.home()`. **Depende de:** 15, 17. **RF:** RF-9, RF-12.
    **Hecho cuando:** las pruebas de T17 pasan y cambiar el directorio de trabajo entre invocaciones cambia el archivo usado.

20. [x] **Aplicar y probar el contrato de errores de almacenamiento** — Asegurar que los fallos de acceso al destino se convierten en el mensaje y código aprobados, sin fallback ni mensaje de éxito. **Depende de:** 16, 18, 19. **RF:** RF-9, RF-11, RF-12.
    **Hecho cuando:** las pruebas de T18 pasan y las operaciones fallidas terminan según el contrato sin crear o modificar archivos fuera del directorio actual.

21. [x] **Verificar aceptación tras el cambio de ubicación** — Ejecutar creación, marcado y listado en un directorio temporal; probar los casos heredados según la decisión aprobada y ejecutar la suite completa. **Depende de:** 19, 20. **RF:** RF-1–RF-12.
    **Hecho cuando:** la demo `add → done → list` usa únicamente el `.habits-cli.json` del directorio de trabajo, cada RF tiene al menos una prueba y `pytest -q` termina en verde.
