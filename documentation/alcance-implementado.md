# Alcance implementado, representado y futuro

## Implementado

### MVP web real

- Aplicación Django 5.2.
- Autenticación y cierre de sesión.
- Catálogos administrables.
- CRUD de novedades con borradores y finalización.
- Fotografía opcional validada y optimizada.
- Histórico, detalle, filtros y estados operacionales.
- Permisos de edición y eliminación.
- Migraciones desde una base vacía.
- 57 pruebas automatizadas.
- Instalación y ejecución local documentadas.

### Entregables de esta etapa

- Repositorio público sanitizado.
- Mockup móvil estático y navegable.
- Diseño responsivo móvil y escritorio.
- Manifiesto y caché estática del prototipo.
- Automatización de CI y GitHub Pages.
- Documentación de arquitectura e integración.

## Representado

Las siguientes funciones aparecen en la interfaz para explicar la experiencia
esperada, pero no constituyen una implementación productiva:

- jornada activa;
- captura desde teléfono;
- guardado local de una novedad;
- estado sin cobertura;
- cola y estados de sincronización;
- resumen manual de jornada;
- comunicación mediante una futura API.

El mockup usa datos ficticios en memoria y los reinicia al recargar.

## Futuro

- Aplicación móvil real.
- Persistencia local de capturas.
- API REST autenticada.
- Sincronización, reintentos e idempotencia operativa.
- Resolución de conflictos entre dispositivos.
- Notificaciones.
- Múltiples fotografías, si el alcance se amplía.
- Funciones de IA en una evaluación posterior y separada.

## Criterio de comunicación

Toda evidencia e informe debe usar las palabras **implementado**,
**representado** o **propuesto** según corresponda. La navegación visible en
GitHub Pages no demuestra que exista un backend móvil ni sincronización real.
