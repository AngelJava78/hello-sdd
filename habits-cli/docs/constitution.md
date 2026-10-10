# Constitución

1. **Stack simple:** Python 3.14+ y biblioteca estándar; pytest solo para pruebas.
2. **Spec antes que código:** todo comportamiento nuevo requiere una spec aprobada antes de implementarse.
3. **Lógica separada:** las reglas de hábitos y rachas no dependen de la CLI ni de la persistencia.
4. **Tests obligatorios:** cada regla nueva tiene pruebas y se ejecuta `pytest -q` antes de integrar cambios.
5. **Persistencia explícita:** los datos se guardan en JSON local; cambiar su formato requiere una spec aprobada.
6. **Idioma consistente:** código e identificadores en inglés; mensajes dirigidos a usuarios en español.