# Contribuir a BitaTurno

## Flujo sugerido

1. Crear una rama breve desde `main`, por ejemplo `feat/nombre-cambio`.
2. Mantener cada commit enfocado en una sola modificación.
3. Ejecutar las comprobaciones antes de solicitar revisión.
4. Abrir un pull request y describir alcance, pruebas y limitaciones.
5. Integrar únicamente después de revisar código y datos incluidos.

## Convención de commits

- `feat:` nueva capacidad.
- `fix:` corrección funcional.
- `docs:` documentación.
- `test:` pruebas o evidencias de validación.
- `ci:` automatización.
- `chore:` mantenimiento sin cambio funcional.

## Pruebas obligatorias

Desde `web/`:

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```

Para cambios en el mockup se debe recorrer al menos Login, Mi jornada, Nueva
captura, Borradores, Completar, Resumen e Histórico, tanto en tamaño móvil como
en escritorio.

Para cambios en `mobile/`:

```text
npm ci
npm run lint
npm run test -- --run
npm run build
```

Los cambios deben respetar el contrato en `documentation/sumativa4/`. Las
modificaciones de dominio, persistencia, estado, rutas, tema o dependencias
requieren una explicación técnica y una prueba del contrato afectado.

## Protección de datos

Solo se permiten datos ficticios. No incorporar:

- bases de datos o archivos `.env`;
- contraseñas, tokens o claves;
- nombres de usuarios operacionales;
- fotografías o registros reales;
- exportaciones, respaldos o registros de ejecución;
- direcciones o configuración de infraestructura privada.

Antes de subir cambios, revisar `git status`, `git diff --cached` y la lista de
archivos versionados.
