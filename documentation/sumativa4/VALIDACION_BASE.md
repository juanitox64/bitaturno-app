# Validación de la base — `0.4.0-rc.1`

Fecha de ejecución: 3 de septiembre de 2026.

## Entorno usado

- Windows PowerShell.
- Python 3.11.9 mediante el entorno virtual del proyecto.
- Django 5.2.16.
- Node.js 24.18.0.
- npm 11.16.0.
- Datos exclusivamente ficticios.

## Instalación reproducible

Desde el archivo de bloqueo se ejecutó:

```text
npm ci --no-audit --no-fund
added 265 packages in 33s
```

La caché, `node_modules` y `dist` están ignorados por Git y no forman parte de la
entrega. En un clon nuevo, `npm ci` requiere acceso al registro de npm.

## Aplicación Ionic

```text
npm run lint
Resultado: OK, 0 errores y 0 advertencias

npm run test -- --run
Test Files  4 passed (4)
Tests       13 passed (13)
Duration    16.54s

npm run build
217 modules transformed
Resultado: OK
```

Vite generó `mobile/dist/`. La salida produjo una advertencia no bloqueante:
el paquete JavaScript principal minificado mide aproximadamente 1.37 MB
(304.39 kB comprimido) y supera el umbral informativo de 500 kB. La división de
código puede evaluarse después de integrar los módulos, sin ampliar esta base.

## Regresión del MVP Django

Los comandos se ejecutaron con `DJANGO_DB_PATH` apuntando a una base SQLite
temporal nueva, eliminada al terminar.

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

python manage.py migrate
Todas las migraciones se aplicaron correctamente desde una base vacía.

python manage.py test
Found 57 test(s).
Ran 57 tests in 17.262s
OK
```

## Regresión del mockup estático

```text
python tests/test_mockup.py
Ran 9 tests in 0.019s
OK
```

## Revisión manual móvil

Se inició Vite temporalmente, se probó en una ventana de 360 × 800 y luego se
cerró el proceso. Se comprobó:

1. redirección de `/` a `/login`;
2. rechazo del formulario de acceso vacío;
3. acceso demostrativo con datos ficticios;
4. Inicio con usuario, contadores y accesos;
5. navegación a Nueva novedad y aviso honesto de funcionalidad en integración;
6. listado y ruta individual de borradores ficticios;
7. acciones de edición y finalización deshabilitadas mientras el módulo está
   incompleto;
8. navegación a Histórico y detalle en integración;
9. estado vacío ante un identificador inexistente;
10. cierre de sesión y nueva protección de rutas internas;
11. ausencia de mensajes en la consola tras habilitar las opciones futuras del
    enrutador;
12. ausencia de desplazamiento horizontal a 360 px.

Evidencias:

- [`base-login-movil.png`](evidencias/base-login-movil.png)
- [`base-inicio-movil.png`](evidencias/base-inicio-movil.png)

## Consideraciones del entorno

- Los comandos Django se ejecutaron explícitamente con el intérprete del entorno
  virtual del proyecto.

## No verificado en esta rama

- GitHub Actions de la nueva aplicación móvil: el workflow está preparado, pero
  requiere subir una rama o abrir un pull request.
- AWS Amplify: existe configuración de build, pero no se realizó despliegue.
- Captura/borradores y histórico/detalle completos: requieren integración
  posterior.
- Autenticación real, API y sincronización remota: no pertenecen a esta base.
