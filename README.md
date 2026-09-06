# BitaTurno `0.4.0-rc.1` — prototipo integrado de Sumativa 4

BitaTurno es una aplicación académica para capturar, completar, consultar y
gestionar novedades asociadas a una jornada de trabajo. Esta etapa continúa el
MVP web Django construido y verificado previamente, conserva el prototipo móvil
navegable v0.3 y añade un prototipo Ionic React con captura, borradores, histórico
y detalle implementados. La aplicación Ionic está publicada en AWS Amplify.

## Problema que aborda

Las observaciones de una jornada pueden quedar dispersas, incompletas o sin una
clasificación uniforme. BitaTurno propone un flujo progresivo: registrar
rápidamente una descripción o fotografía, conservarla como borrador, completar
su clasificación y consultarla después en una bitácora.

## Objetivo

Mantener el MVP web y ofrecer un prototipo móvil para capturar novedades,
recuperar borradores, completar su clasificación y consultar el histórico.
El prototipo Ionic conserva los datos en el navegador; la integración con Django
por API y la sincronización entre dispositivos permanecen como trabajo futuro.

## Accesos públicos

- Aplicación Ionic en AWS Amplify: <https://main.d1kt5hvps8dfnb.amplifyapp.com/>
- Repositorio: <https://github.com/juanitox64/bitaturno-app>
- Mockup móvil: <https://juanitox64.github.io/bitaturno-app/>

AWS Amplify publica la aplicación Ionic desde `mobile/`; sus registros se guardan
en el mismo navegador mediante `localStorage`. GitHub Pages conserva el mockup
estático v0.3. Ninguno de esos dos sitios ejecuta Django ni utiliza una base de
datos remota.

## Estado de los componentes

| Componente | Estado verificado al 6 de septiembre de 2026 |
|---|---|
| MVP Django | Existente y conservado |
| Mockup estático v0.3 | Existente |
| Prototipo Ionic v0.4 | Implementado e integrado |
| Login e inicio Ionic | Implementados |
| Persistencia local común | Implementada |
| Captura y borradores | Implementados e integrados mediante PR #2 |
| Histórico y detalle | Implementados e integrados mediante PR #3 |
| Integración con API remota | No implementada |
| Despliegue AWS Amplify | Implementación de `main` realizada |
| Publicación nativa | Fuera del alcance |

## Funciones reales del MVP web

- Inicio y cierre de sesión con usuarios Django.
- Administración de catálogos y cuentas desde Django Admin.
- Formulario progresivo para guardar borradores o finalizar registros.
- Fotografía opcional JPEG, PNG o WEBP con validación y optimización.
- Edición y eliminación confirmada de borradores propios.
- Histórico de novedades registradas.
- Filtros por disciplina, turno, prioridad y estado operacional.
- Cambio separado del estado operacional y fechas de cierre.
- Contadores de registradas, pendientes, en revisión, cerradas y borradores.
- Permisos para proteger borradores ajenos y registros finalizados.
- Transferencia portable administrada, con inspección y simulación previa.
- 57 pruebas automatizadas.

El código real se encuentra en [`web/`](web/).

## Funciones representadas en el mockup

El prototipo disponible en [`docs/`](docs/) representa:

- inicio de sesión demostrativo;
- vista **Mi jornada**;
- captura rápida de texto y fotografía;
- borradores y clasificación posterior;
- estados de conectividad y sincronización simulados;
- resumen manual de jornada;
- histórico, filtros y detalle.

La PWA almacena en caché los archivos estáticos para permitir navegación básica
después de la primera carga. No conserva capturas reales ni sincroniza datos.

## Tecnologías

- Python 3.11 compatible.
- Django 5.2 LTS.
- SQLite para ejecución local.
- Pillow para validación y optimización de imágenes.
- HTML, CSS y JavaScript sin frameworks ni CDN para el mockup.
- GitHub Actions para pruebas y GitHub Pages.
- Ionic 9, React 19, TypeScript y Vite para la base híbrida.
- `localStorage` detrás de una interfaz de repositorio para el prototipo móvil.

## Estructura

```text
bitaturno-app/
├── web/                    # MVP Django real
├── docs/                   # Mockup móvil publicado en Pages
├── mobile/                 # Base Ionic React 0.4.0-rc.1
├── documentation/          # Arquitectura, alcance, pruebas y evidencias
├── .github/workflows/      # CI y despliegue del sitio estático
├── amplify.yml             # Build del frontend Ionic en AWS Amplify
├── requirements.txt
└── requirements-lock.txt
```

## Instalación local del MVP web

### Windows PowerShell

```powershell
git clone https://github.com/juanitox64/bitaturno-app.git
Set-Location .\bitaturno-app
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
Set-Location .\web
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py createsuperuser
..\.venv\Scripts\python.exe manage.py runserver
```

Abrir <http://127.0.0.1:8000/>. Para detener el servidor, presionar `Ctrl+C`.

### Linux o macOS

```bash
git clone https://github.com/juanitox64/bitaturno-app.git
cd bitaturno-app
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements-lock.txt
cd web
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py createsuperuser
../.venv/bin/python manage.py runserver
```

## Variables de entorno

La ejecución local con `DJANGO_DEBUG=1` genera una clave efímera y no necesita
un archivo `.env`. Para una configuración persistente, usar `.env.example` como
referencia y definir una clave propia fuera del repositorio.

Nunca se debe versionar `.env`, bases de datos, fotografías, exportaciones ni
credenciales.

## Pruebas

Los comandos deben ejecutarse desde `web/` para que Django descubra toda la
batería:

```powershell
Set-Location .\web
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py test
```

El resultado esperado es `57 test(s)` y `OK`.

## Aplicación híbrida Ionic

Desde la raíz del repositorio:

```powershell
Set-Location .\mobile
npm ci
npm run lint
npm run test -- --run
npm run build
npm run dev
```

La aplicación implementa sesión demostrativa, Inicio con contadores, captura,
listado y edición de borradores, eliminación confirmada, finalización, histórico
con buscador y filtros, detalle y manejo de identificadores inexistentes.
Todos los módulos usan el dominio y la persistencia local comunes.

Al finalizar una captura, su estado operacional pasa a `pendiente`; por eso puede
aparecer como pendiente dentro del histórico de capturas finalizadas.

Validación de la versión integrada `e4c8cdb7` de `main`:

- Ionic: 24 pruebas en 7 archivos, lint y build aprobados.
- Django: 57 pruebas y comprobaciones del proyecto aprobadas.
- Mockup estático: 9 pruebas aprobadas.
- Total: 90 pruebas automatizadas aprobadas.

Ejecuciones de referencia:
[Ionic](https://github.com/juanitox64/bitaturno-app/actions/runs/34011536203) y
[Django / mockup](https://github.com/juanitox64/bitaturno-app/actions/runs/34011536205).

Las instrucciones colaborativas están en
[`documentation/sumativa4/`](documentation/sumativa4/) y los resultados de la
base están registrados en
[`VALIDACION_BASE.md`](documentation/sumativa4/VALIDACION_BASE.md).

## Servir el mockup localmente

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m http.server 8080 --directory docs
```

Abrir <http://127.0.0.1:8080/>. Servirlo por HTTP permite comprobar también el
registro del service worker.

## Integración móvil/web propuesta

La evolución prevista utiliza una aplicación móvil para captura y consulta
rápida, una cola local para conectividad intermitente, una API REST futura y el
backend Django como servicio central. Los UUID ya presentes en el dominio
permiten proponer idempotencia y prevención de duplicados.

La propuesta completa se encuentra en
[`documentation/integracion-movil-web.md`](documentation/integracion-movil-web.md).

## Limitaciones

- El mockup no autentica usuarios ni envía información.
- Los datos del mockup estático son ficticios y se reinician al recargar; los
  datos ficticios de Ionic sí persisten localmente en el mismo navegador.
- No existe API REST en esta entrega.
- No existe cola de sincronización ni garantía de operación offline de Ionic.
- La PWA corresponde únicamente al sitio estático demostrativo.
- El MVP usa SQLite y admite una fotografía por novedad.
- La base Ionic no tiene API, sincronización remota ni autenticación real.
- Los registros de Ionic no se comparten entre navegadores ni se respaldan en AWS.
- Django no está desplegado en la URL de Amplify.
- Las fotografías y el cambio operacional de estados pertenecen al MVP Django;
  no se presentan como funcionalidades implementadas en Ionic.

## Mejoras futuras

- API autenticada y versionada.
- Sincronización idempotente y resolución de conflictos.
- Notificaciones y trazabilidad ampliada.
- Múltiples fotografías, sujeto a una revisión del alcance.
- Funciones de IA únicamente en una etapa posterior y fuera de esta entrega.

