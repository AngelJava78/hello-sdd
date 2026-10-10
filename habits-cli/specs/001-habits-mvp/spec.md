# Spec 001 — MVP de habits-cli

## Contexto y objetivo
Los estudiantes de programación abandonan hábitos de estudio por falta de
seguimiento. habits-cli permite registrar hábitos y ver la racha de días
consecutivos desde la terminal, sin fricción, para reforzar la constancia.

## Usuarios
Estudiantes y desarrolladores que viven en la terminal. Un solo usuario por
máquina; sin cuentas ni sincronización.

## Historias de usuario
- H1: Como estudiante quiero crear hábitos con un nombre para tener la lista
  de lo que quiero trabajar cada día.
- H2: Como estudiante quiero marcar un hábito como hecho hoy para registrar
  mi constancia.
- H3: Como estudiante quiero ver mis hábitos con su racha actual para
  motivarme a no romperla.

## Requisitos funcionales (criterios de aceptación en EARS)

### Crear hábito (H1)
- RF-1: CUANDO el usuario ejecute `habits add <nombre>` con un nombre no
  vacío que no exista, EL SISTEMA creará el hábito y lo confirmará con un
  mensaje (salida 0).
- RF-2: SI el nombre ya existe (comparación ignorando mayúsculas/minúsculas
  y espacios al inicio o final), ENTONCES EL SISTEMA no creará un duplicado
  e informará del conflicto (salida 1).
- RF-3: SI el nombre está vacío o son solo espacios, ENTONCES EL SISTEMA
  rechazará la orden con un mensaje de error (salida 1).

### Marcar como hecho (H2)
- RF-4: CUANDO el usuario ejecute `habits done <nombre>` y el hábito exista,
  EL SISTEMA registrará la fecha actual como completada y lo confirmará
  (salida 0).
- RF-5: SI el hábito ya está completado hoy, ENTONCES EL SISTEMA lo
  comunicará sin duplicar el registro (operación idempotente, salida 0).
- RF-6: SI el hábito no existe, ENTONCES EL SISTEMA mostrará un error
  sugiriendo consultar `habits list` (salida 1).
- RF-13: CUANDO el usuario ejecute `habits done <nombre> --ayer` y el hábito
  exista, EL SISTEMA registrará la fecha de ayer como completada y confirmará
  el registro (salida 0); SI ese hábito ya estaba completado ayer, ENTONCES EL
  SISTEMA informará que ya estaba marcado, no duplicará la fecha y terminará
  con salida 0. El registro de ayer contará como completado para el cálculo de
  racha según RF-10.

### Listar con rachas (H3)
- RF-7: CUANDO el usuario ejecute `habits list`, EL SISTEMA mostrará cada
  hábito con su racha actual en días, ordenados por racha descendente y,
  a igualdad, por nombre alfabético (salida 0).
- RF-8: MIENTRAS no exista ningún hábito, EL SISTEMA responderá a
  `habits list` con un mensaje invitando a crear el primero (salida 0).

### Reglas transversales
- RF-9: EL SISTEMA almacenará todos los datos en un único archivo JSON local
  legible por humanos.
- RF-10: EL SISTEMA calculará la racha como el número de días consecutivos
  completados cuyo último día sea hoy o ayer; si el último registro es
  anterior a ayer, la racha es 0.
- RF-11: SI el archivo de datos existe pero no es JSON válido, ENTONCES EL
  SISTEMA abortará con un mensaje claro y NO sobrescribirá el archivo
  (salida 1).
- RF-12: CUANDO EL SISTEMA lea o guarde datos de hábitos, DEBERÁ usar el archivo
  `.habits-cli.json` en el directorio de trabajo actual desde el que se ejecuta
  la aplicación de Python, y NO deberá usar `Path.home()` como ubicación.

## Requisitos no funcionales
- Respuesta inmediata (<1 s) en equipos modestos. Sin acceso a red.
- Multiplataforma: macOS, Linux y Windows.
- Mensajes al usuario en español, claros y accionables.

## Casos límite ya cubiertos
- Doble `done` el mismo día → RF-5.
- `done <nombre> --ayer` y la fecha de ayer ya está registrada: se conserva una
  sola marca, se informa que ya estaba marcada y termina con salida 0 (RF-13).
- Marcar ayer cuando también hay marcas consecutivas anteriores: la marca
  añadida puede extender o mantener la racha según la secuencia de fechas de
  RF-10; si hoy ya está marcado, no se crea un hueco por registrar ayer.
- Combinaciones de `--ayer` con argumentos ausentes, nombres vacíos o varias
  opciones de fecha incompatibles:
  [NECESITA ACLARACIÓN] definir validación y precedencia.
- Interpretación de “ayer” al cruzar mes/año o cambio de hora:
  [NECESITA ACLARACIÓN] se debe especificar con respecto a la fecha local
  actual que ya usa RF-10.
- Racha con hueco de más de un día → RF-10 (racha 0).
- Hecho ayer pero aún no hoy → RF-10 (la racha se conserva).
- Archivo inexistente → se crea estructura vacía (parte de RF-9).
- Archivo corrupto → RF-11.
- Si no se puede leer o escribir en el directorio de trabajo actual, el sistema
  informa el error en español, termina con código 1, no confirma éxito y no
  recurre a `Path.home()`.
- La aplicación se ejecuta desde directorios de trabajo distintos: cada
  ejecución buscará el archivo en el directorio desde el que se invocó.
- Existe un `.habits-cli.json` con datos en `Path.home()` y el destino nuevo no
  existe, o ambos contienen datos distintos: el sistema usa exclusivamente el
  archivo del directorio de trabajo; el archivo de home queda intacto y no se
  migra ni combina automáticamente.

## Fuera de alcance (MVP)
Editar, renombrar o borrar hábitos; marcar fechas pasadas; estadísticas;
colores; recordatorios; sincronización; interfaz TUI.

## Criterios de finalización
- Todos los RF cubiertos por al menos un test automático y `pytest -q` en verde.
- Demo manual del flujo add → done → list sin errores.

## Dudas abiertas
- Ninguna para RF-12: los datos previos en `Path.home()` no se migran ni se
  combinan y se dejan intactos; un error de acceso al destino produce un
  mensaje en español y código 1 sin fallback.