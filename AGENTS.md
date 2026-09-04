# AGENTS.md — BitaTurno colaborativo

## Propósito y carpetas

- `web/`: MVP Django existente. Conservar su comportamiento, migraciones y pruebas.
- `docs/`: mockup estático v0.3 publicado mediante GitHub Pages.
- `mobile/`: base híbrida Ionic React de la Sumativa 4.
- `documentation/`: alcance, arquitectura, pruebas y guías de colaboración.
- `.github/workflows/`: CI de Django, Pages y aplicación móvil.

## Instalación

Backend desde la raíz:

```text
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
```

Aplicación móvil:

```text
cd mobile
npm ci
```

## Comandos obligatorios

Django, desde `web/`:

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```

Ionic, desde `mobile/`:

```text
npm ci
npm run lint
npm run test -- --run
npm run build
npm run dev
```

## Convención y colaboración

- Usar commits breves: `feat:`, `fix:`, `docs:`, `test:`, `ci:` o `chore:`.
- No realizar commits en nombre de otra persona.
- No fusionar a `main` sin revisión.
- `domain/`, `infrastructure/`, `state/`, rutas, configuración y tema son archivos comunes.
- Los módulos funcionales viven en `mobile/src/features/` y deben respetar el
  contrato técnico común.
- Un cambio necesario en un archivo común se documenta y revisa antes de integrarlo.

## Datos y declaraciones

- Usar únicamente datos ficticios.
- No incorporar `.env`, bases, fotografías, exportaciones, credenciales, tokens,
  claves, direcciones privadas ni datos empresariales reales.
- No guardar contraseñas en `localStorage` o `sessionStorage`.
- No declarar API, sincronización, modo offline avanzado, aplicación nativa o
  despliegue cloud mientras no existan y hayan sido probados.
- No reemplazar ni reescribir el MVP Django o el mockup v0.3.

## Criterio de terminado

Un cambio está listo para revisión solo si compila, sus pruebas aplicables pasan,
no deja errores de lint, conserva los flujos previos y documenta cualquier límite.
Antes de abrir un pull request se debe revisar `git status`, el diff completo, los
datos incluidos y ejecutar los comandos móviles y/o Django correspondientes.
