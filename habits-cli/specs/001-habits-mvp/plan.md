# Plan técnico: MVP de habits-cli

## Alcance y trazabilidad

Este plan describe el QUÉ técnico para implementar la spec, sin cambiarla ni
escribir código. Respeta la constitución: Python 3.14+ y biblioteca estándar,
pytest solo para tests, lógica independiente de CLI y persistencia, datos en
JSON local, tests para cada regla y mensajes al usuario en español. Cada sección
indica los RF que cubre.

## Estructura de módulos

| Módulo | Responsabilidad | RF cubiertos |
| --- | --- | --- |
| `habits/core.py` | Reglas puras: normalización de nombres, creación, marcado diario, cálculo de racha y preparación del listado. No lee/escribe archivos ni presenta mensajes. | RF-1–RF-8, RF-10 |
| `habits/storage.py` | Leer y guardar el modelo JSON; resolver el archivo de datos desde el directorio de trabajo actual; reportar JSON inválido y errores de acceso sin sobrescribir datos inválidos. | RF-9, RF-11, RF-12 |
| `habits/cli.py` | Parsear comandos, coordinar núcleo y almacenamiento, presentar resultados en español y devolver códigos de salida del contrato. | RF-1–RF-8, RF-11, RF-12 |
| `habits/__main__.py` | Punto de entrada de `python -m habits`; delegar en la CLI y propagar el código de salida. | RF-1–RF-8, RF-11, RF-12 |
| `tests/` | Tests unitarios del núcleo, tests de almacenamiento aislados y tests de CLI/flujo completo. | RF-1–RF-12 |

La dirección de dependencias será CLI → núcleo y CLI → almacenamiento. Núcleo
no importará CLI ni almacenamiento. Así las reglas de hábitos y rachas pueden
probarse sin interacción de terminal ni efectos de archivo (constitución,
principio 3).

## Modelo de datos JSON

Un único archivo local legible por humanos, `.habits-cli.json`, en el
directorio de trabajo actual desde el que se ejecuta la aplicación de Python.
La resolución del directorio de trabajo y el nombre de archivo cubren RF-9 y
RF-12; no se usará `Path.home()` como ubicación ni se recurrirá allí
silenciosamente.

```json
{
  "habits": [
    {
      "name": "Leer apuntes",
      "completed_dates": [
        "2026-10-09",
        "2026-10-10"
      ]
    }
  ]
}
```

- `habits` es una lista; cada elemento contiene el nombre visible y una lista de
  fechas completadas. Los nombres se comparan tras recortar espacios iniciales
  y finales e ignorar mayúsculas/minúsculas (RF-1, RF-2, RF-3).
- `completed_dates` usa fechas locales de calendario ISO `YYYY-MM-DD`, sin
  duplicados para un hábito (RF-4, RF-5, RF-10).
- Si el archivo del directorio de trabajo no existe, se interpreta como lista
  vacía; se crea al guardar el primer cambio (RF-8, RF-9, RF-12).
- Si existe pero no es JSON válido, o no cumple el esquema esperado, se reporta
  error y no se sobrescribe (RF-11).
- Las escrituras se preparan en un archivo temporal junto al destino y se
  sustituyen al terminar; un error previo al reemplazo conserva el archivo
  existente y no se informa éxito (RF-1, RF-4, RF-11, RF-12).

**Datos previos en `Path.home()`:** la spec establece que el archivo antiguo se
ignora y queda intacto; no se migra ni combina con el archivo del directorio
actual. Si hay archivos en ambas ubicaciones, solo se usa el del directorio de
trabajo (RF-12).

**Directorio sin acceso:** un error de lectura o escritura se comunica en
español, devuelve código 1, no afirma éxito y no usa `Path.home()` como
fallback (RF-9, RF-12).

## Algoritmo de cálculo de racha

Se comparan fechas de calendario locales, no intervalos de 24 horas. El dato
`hoy` se obtiene de la fecha local y se pasa como entrada a la función pura para
que las pruebas no dependan del reloj real. Los días de mes/año se recorren
mediante aritmética de calendario (RF-4, RF-10).

```text
calcular_racha(fechas_completadas, hoy):
    completadas = conjunto(fechas_completadas)

    si hoy pertenece a completadas:
        fecha = hoy
    si no, si ayer(hoy) pertenece a completadas:
        fecha = ayer(hoy)
    si no:
        devolver 0

    racha = 0
    mientras fecha pertenece a completadas:
        racha = racha + 1
        fecha = día_anterior(fecha)

    devolver racha
```

La última marca debe ser hoy o ayer para iniciar la cuenta; cualquier hueco
interrumpe la secuencia. Una lista vacía devuelve cero (RF-10).

## Contrato de la CLI

La invocación de referencia es `python -m habits`.

| Comando | Comportamiento y salida | Código | RF cubiertos |
| --- | --- | --- | --- |
| `python -m habits add "<nombre>"` | Crea el hábito sin marcas y confirma en español. Rechaza nombre vacío o solo espacios, y duplicado tras normalizar mayúsculas y espacios periféricos; errores en español. | 0 éxito; 1 validación/duplicado | RF-1, RF-2, RF-3 |
| `python -m habits done "<nombre>"` | Registra la fecha local actual y confirma. Si ya estaba marcado hoy, informa que ya estaba marcado, sin duplicar. Para un hábito inexistente indica consultar `python -m habits list`. | 0 marcado o ya marcado; 1 no existe | RF-4, RF-5, RF-6 |
| `python -m habits list` | Muestra cada nombre y racha en días, ordenado por racha descendente y nombre alfabético ascendente para empates. Si está vacío, invita a crear el primer hábito. | 0 | RF-7, RF-8, RF-10 |

Los éxitos e información (creación, marcado, ya marcado y resultados de lista)
van a salida estándar; errores a salida de error. Todo texto dirigido al
usuario está en español (constitución, principio 6).

| Error | Resultado esperado | Código | RF |
| --- | --- | --- | --- |
| JSON inválido | Mensaje claro; se aborta y el archivo permanece intacto. | 1 | RF-11 |
| No se puede leer/escribir el archivo del directorio de trabajo | Mensaje de error en español, sin éxito falso; no fallback a `Path.home()`. | 1 | RF-9, RF-12 |
| Comando/argumentos inválidos | Uso y error en español. | 2 | Contrato CLI |

## Decisiones técnicas justificadas

| Decisión | Justificación | Alternativa descartada |
| --- | --- | --- |
| Solo biblioteca estándar para producto; pytest para pruebas. | Respeta la constitución y reduce dependencias/conceptos en un proyecto educativo. | Framework de CLI, ORM o bibliotecas externas: añadirían dependencias innecesarias. |
| Mantener núcleo puro separado de CLI y almacenamiento. | Cumple el principio de separación y permite probar las reglas sin archivos ni terminal. | Incluir rachas en CLI o acceso a archivos en el núcleo: mezcla responsabilidades. |
| Un JSON único, legible y local, con fechas ISO. | Cumple RF-9 y el esquema explícito; resulta inspeccionable y simple de mantener. | Base de datos o un archivo por hábito: más conceptos y distinto formato/alcance. |
| Resolver `.habits-cli.json` en el directorio de trabajo actual. | Cumple RF-12 y evita que los datos dependan de `Path.home()`; cada invocación desde otro directorio lee/escribe en ese directorio. | Guardar en `Path.home()` o en el directorio del paquete: ambos contradicen el requisito de ubicación en el directorio de ejecución. |
| Dejar intactos y no migrar los datos preexistentes de `Path.home()`. | La spec dispone que solo se use el archivo del directorio de trabajo; preservar el archivo anterior evita pérdida y no mezcla perfiles/datos sin autorización. | Migración o combinación automática: contradice la decisión especificada y puede duplicar o sobrescribir datos. |
| Fechas de calendario local y marca idempotente diaria. | La funcionalidad y la racha son por día; evita duplicados y diferencias por duración del día (RF-4, RF-5, RF-10). | Timestamps UTC o ventanas de 24 horas: pueden desplazar el día local y distorsionar rachas. |
| Guardado temporal con reemplazo al final. | Reduce el riesgo de truncar el archivo existente durante una interrupción; reporta errores explícitamente. | Sobrescritura directa: puede dejar datos incompletos. |
| Propagar fallos de acceso como error en español y código 1, sin fallback. | Conserva la ubicación exigida por RF-12 y evita que parezca que se guardó en otra carpeta. | Cambiar silenciosamente a home: contradice RF-12 y vuelve confuso dónde quedan los datos. |

## Estrategia de tests

Cada RF debe contar con cobertura automatizada. Usar pytest y ejecutar `pytest
-q` antes de integrar cambios (constitución). Las pruebas no acceden al archivo
real del usuario, a la red ni dependen del reloj del sistema.

| Cobertura y casos | RF |
| --- | --- |
| Crear nombre válido y conservarlo; confirmar éxito/código 0. | RF-1 |
| Duplicado variando mayúsculas o espacios iniciales/finales; rechazo/código 1 y datos intactos. | RF-2 |
| Nombre vacío, espacios solamente y cadena vacía por parser/CLI; rechazo/código 1, no se guarda. | RF-3 |
| Marcar hábito existente con fecha controlada; comprobar fecha persistida y confirmación/código 0. | RF-4 |
| Marcar dos veces el mismo día; misma única fecha, aviso idempotente y código 0. | RF-5 |
| Marcar nombre inexistente; error, sugerencia de `list`, código 1 y datos sin cambio. | RF-6 |
| Lista con rachas diferentes y empatadas; validar valor, orden y código 0. | RF-7 |
| Lista sin hábitos; validar invitación y código 0. | RF-8 |
| Archivo del directorio de trabajo ausente, lectura/escritura JSON legible UTF-8 y conservación entre invocaciones. | RF-9 |
| Racha con marca hoy, ayer, días continuos, hueco, registro antiguo, cero marcas y cruce de mes/año. | RF-10 |
| JSON sintácticamente inválido, codificación no UTF-8 y estructura incorrecta; error, código 1 y bytes originales sin cambios. | RF-11 |
| Cambiar el directorio de trabajo a dos directorios temporales y comprobar que cada uno usa su `.habits-cli.json`, sin leer/escribir en `Path.home()`. | RF-12 |
| Fallo de acceso al leer/escribir el destino; verificar mensaje en español, código 1, sin éxito falso ni fallback a home. | RF-9, RF-12 |
| Archivo preexistente en home o archivos distintos en home y cwd: comprobar que home queda intacto y solo se usa cwd; no migrar ni combinar. | RF-12 |
| Demo de aceptación en directorio temporal: `add → done → list`. | RF-1–RF-10, RF-12 |

La verificación de multiplataforma y el requisito de respuesta inferior a un
segundo requieren validación en los entornos correspondientes; las pruebas
locales no deben interpretarse como evidencia de ejecución en todos los
sistemas (RNF).
