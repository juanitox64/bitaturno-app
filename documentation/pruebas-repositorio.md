# Pruebas del repositorio público

## Resumen

El repositorio se validó localmente, en GitHub Actions, en GitHub Pages y desde
un clon temporal completamente limpio. Las pruebas usaron exclusivamente datos
ficticios y una base SQLite nueva.

Fecha de comprobación: 24 de agosto de 2026.

## Pruebas previas a la publicación

La copia pública del MVP se ejecutó con almacenamiento temporal separado.

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

python manage.py migrate --noinput
Todas las migraciones aplicadas correctamente desde una base vacía.

python manage.py test
Found 57 test(s).
Ran 57 tests in 15.927s
OK
```

## Mockup local

La navegación se sirvió temporalmente por HTTP y se comprobó en 390 × 844 y en
escritorio. El recorrido verificado fue:

```text
Inicio de sesión
→ Mi jornada
→ Nueva captura
→ Mis borradores
→ Completar novedad
→ Histórico
```

También se verificaron el resumen manual, la validación de campos obligatorios,
los filtros del histórico y el detalle. Los nueve recursos estáticos respondieron
HTTP 200 y la consola no presentó errores ni advertencias.

La revisión visual detectó inicialmente que la barra inferior podía mostrarse
en el login. Se corrigió y la prueba estructural confirma que permanece oculta
antes del ingreso.

## Pruebas automatizadas del mockup

El archivo `tests/test_mockup.py` valida:

1. existencia de archivos obligatorios;
2. presencia de las siete pantallas;
3. destinos de navegación válidos;
4. barra inferior oculta en el login;
5. ausencia de dependencias externas;
6. referencias locales existentes;
7. manifiesto e iconos válidos;
8. archivos incluidos en la caché estática;
9. rotulación explícita del alcance.

Resultado local y en CI:

```text
Ran 9 tests
OK
```

## GitHub Actions

El workflow ejecuta en cada push y pull request:

- instalación de dependencias fijadas;
- migraciones sobre SQLite temporal;
- `manage.py check`;
- 57 pruebas Django;
- 9 pruebas del mockup;
- comprobación de migraciones pendientes.

La primera definición de CI fue rechazada antes de crear trabajos porque usaba
un contexto temporal aún no disponible al evaluar el workflow. Se reemplazaron
esas rutas por ubicaciones temporales explícitas. Las ejecuciones posteriores
quedaron aprobadas.

Ejecución funcional registrada:

```text
Pruebas del MVP web
Run 32693419867
Resultado: success
Duración del trabajo: 21 s
```

## GitHub Pages

El workflow oficial publicó exclusivamente `docs/`.

```text
Publicar mockup en GitHub Pages
Run 32693419890
Resultado: success
```

URL comprobada:

<https://juanitox64.github.io/bitaturno-app/>

Se confirmó HTTP 200 para:

- página principal e `index.html`;
- CSS y JavaScript;
- manifest;
- service worker;
- dos iconos;
- imagen ficticia de evidencia.

Las rutas funcionan bajo `/bitaturno-app/`, se fuerza HTTPS y no se observaron
errores de consola.

## Validación desde clon limpio

Se clonó `https://github.com/juanitox64/bitaturno-app.git` en una carpeta temporal
sin reutilizar archivos del proyecto de origen.

Resultados reales:

```text
Entorno virtual nuevo: OK
Dependencias desde requirements-lock.txt: OK
check: sin observaciones
makemigrations --check --dry-run: No changes detected
migrate desde base vacía: OK
57 pruebas Django: OK (15.084 s)
9 pruebas del mockup: OK (0.018 s)
MVP iniciado temporalmente: HTTP 200
Mockup servido temporalmente: HTTP 200
Procesos temporales detenidos: sí
Carpeta temporal eliminada: sí
```

## PWA estática

El service worker utiliza red primero y caché como respaldo. La lista del
shell estático y la actualización de versión se validan automáticamente.

No se activó una simulación controlada de pérdida total de red en el navegador
público. Por ello, la evidencia confirma la configuración de caché y la
navegación online, pero no se presenta como prueba de una aplicación móvil
offline. En cualquier caso, las capturas del mockup no se persisten ni se
sincronizan realmente.

## Base Ionic de Sumativa 4

El 3 de septiembre de 2026 se agregó una base Ionic independiente del mockup y
del MVP Django. La regresión local confirmó:

```text
npm ci: 265 paquetes instalados desde el archivo de bloqueo
npm run lint: OK, sin advertencias
npm run test -- --run: 13 pruebas, OK (16.54 s)
npm run build: OK
python tests/test_mockup.py: 9 pruebas, OK (0.019 s)
python manage.py check: sin observaciones
python manage.py makemigrations --check --dry-run: No changes detected
python manage.py migrate: todas las migraciones aplicadas desde una base vacía
python manage.py test: 57 pruebas, OK (17.262 s)
```

También se recorrieron manualmente Login, Inicio, captura, borradores,
histórico, detalle, cierre de sesión, rutas protegidas e identificador
inexistente en una ventana de 360 × 800. La consola quedó sin mensajes y no se
detectó desplazamiento horizontal.

El build presenta una advertencia no bloqueante por un paquete JavaScript
minificado mayor a 500 kB. La autenticación real, los módulos funcionales de
captura e histórico y el despliegue AWS permanecen fuera de la rama base.

El registro completo se conserva en
[`sumativa4/VALIDACION_BASE.md`](sumativa4/VALIDACION_BASE.md).
