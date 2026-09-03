# Plan de integración — Sumativa 4

## Orden

1. Revisar la rama base `feat/s4-base-ionic`.
2. Confirmar `npm ci`, lint, 13 pruebas base y build.
3. Integrar la base a la rama acordada por el equipo.
4. Implementar captura y borradores en una rama técnica separada.
5. Revisar e integrar el módulo de captura.
6. Actualizar la rama del histórico desde la base ya integrada.
7. Resolver conflictos conservando el contrato común.
8. Revisar e integrar histórico y detalle.
9. Ejecutar la regresión completa y preparar el despliegue autorizado.

Cada cambio debe conservar un alcance técnico identificable y resultados de
pruebas reproducibles.

## Revisión del módulo de captura

- Verificar que el cambio respete los límites del módulo y el contrato común.
- Confirmar que no use directamente `localStorage`.
- Revisar creación, edición sin duplicación, finalización y eliminación confirmada.
- Recargar el navegador y comprobar persistencia.
- Ejecutar lint, pruebas y build desde una instalación limpia.
- Revisar evidencias móviles y datos ficticios.

## Integración secuencial

El módulo de histórico debe actualizarse desde la rama que ya contiene la base y
el módulo de captura integrado. Los conflictos se resuelven en Git y las
comprobaciones se repiten antes de continuar; no se copian archivos manualmente
entre ramas.

## Revisión del módulo de histórico

- Verificar límites de archivos y contrato común.
- Confirmar que el histórico excluya borradores.
- Probar cada filtro y sus combinaciones.
- Abrir detalles y un identificador inexistente.
- Revisar el hallazgo real corregido y su evidencia antes/después.
- Ejecutar lint, pruebas y build desde una instalación limpia.

## Pruebas después de cada integración

Desde `mobile/`:

```text
npm ci
npm run lint
npm run test -- --run
npm run build
```

Desde `web/`, usando el Python del entorno:

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```

## Matriz mínima de regresión

| Flujo | Base | Tras captura | Tras histórico |
|---|---:|---:|---:|
| Login demostrativo válido | Sí | Repetir | Repetir |
| Login vacío rechazado | Sí | Repetir | Repetir |
| Cierre de sesión | Sí | Repetir | Repetir |
| Inicio y contadores | Sí | Repetir | Repetir |
| Crear borrador | Pendiente | Probar | Repetir |
| Editar sin duplicar | Pendiente | Probar | Repetir |
| Finalizar a pendiente | Contrato | Probar | Repetir |
| Eliminar con confirmación | Pendiente | Probar | Repetir |
| Histórico sin borradores | Pendiente | — | Probar |
| Filtros combinados | Pendiente | — | Probar |
| Detalle e ID inexistente | Pendiente | — | Probar |
| Persistencia tras recarga | Repositorio | Probar | Repetir |
| Vista de 360 px | Base | Probar | Probar |
| Django: 57 pruebas | Sí | Repetir | Repetir |

## Evidencia para el informe

Conservar:

- URL y número de cada PR;
- ramas, commits y alcance de cada cambio;
- revisiones o comentarios relevantes;
- resultados completos de CI;
- capturas de Login, Inicio, Captura, Borradores, Histórico y Detalle;
- prueba de persistencia tras recargar;
- evidencia del hallazgo corregido;
- evidencia real del despliegue cuando exista;
- limitaciones y pruebas no ejecutadas.

No incluir contraseñas, tokens, direcciones privadas ni datos reales.

## Reversión

Si un PR rompe lint, pruebas, compilación o navegación:

1. detener su integración o revertir únicamente el merge problemático;
2. conservar la rama y los commits para diagnóstico;
3. adjuntar la salida exacta del error;
4. crear una rama de corrección desde el último commit aprobado;
5. aplicar el cambio mínimo y repetir toda la matriz afectada;
6. no reescribir el historial ni eliminar evidencia del fallo.
