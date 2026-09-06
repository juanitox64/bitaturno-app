# BitaTurno móvil — prototipo integrado `0.4.0-rc.1`

Aplicación académica construida con Ionic, React y TypeScript. Se ejecuta en
navegador y está publicada en
[AWS Amplify](https://main.d1kt5hvps8dfnb.amplifyapp.com/).

## Estado real

Implementado e integrado en `main`:

- navegación para siete rutas y protección mediante sesión demostrativa;
- login, cierre de sesión e inicio con contadores y accesos;
- modelo `Novedad`, validaciones comunes y proveedor `useNovedades`;
- creación, listado, búsqueda, edición y eliminación confirmada de borradores;
- finalización de la captura y traslado al histórico;
- histórico con búsqueda y filtros por disciplina, prioridad y estado;
- detalle y manejo de identificadores inexistentes, con retorno al histórico;
- persistencia local, datos ficticios iniciales y restablecimiento de demostración.

La captura completada recibe estado operacional `pendiente`. Estar finalizada
no equivale a tener el estado operacional cerrado.

## Requisitos

- Node.js 24 compatible.
- npm 11 o compatible con el archivo de bloqueo.

## Instalación y ejecución

Desde `mobile/`:

```text
npm ci
npm run dev
```

Abrir la dirección local indicada por Vite. El acceso acepta cualquier usuario y
contraseña ficticios no vacíos. La contraseña se descarta y la sesión se
conserva en `sessionStorage`; no existe autenticación real.

## Validación

Desde `mobile/`:

```text
npm ci
npm run lint
npm run test -- --run
npm run build
```

El commit integrado `e4c8cdb7` obtuvo 24 pruebas aprobadas en 7 archivos, lint y
build aprobados. El resultado está en
[GitHub Actions, ejecución 34011536203](https://github.com/juanitox64/bitaturno-app/actions/runs/34011536203).
La salida estática se genera en `mobile/dist/`.

## Rutas

| Ruta | Función implementada |
|---|---|
| `/login` | Acceso demostrativo |
| `/inicio` | Contadores y accesos |
| `/nueva` | Crear borrador |
| `/borradores` | Listar y buscar borradores |
| `/borradores/:id` | Editar, finalizar o eliminar con confirmación |
| `/historico` | Buscar y filtrar novedades finalizadas |
| `/historico/:id` | Detalle o aviso de registro inexistente |

## Persistencia y límites

La clave es `bitaturno:novedades:v1`. El repositorio síncrono está aislado
mediante `NovedadRepository`, de modo que una API futura pueda sustituir la
infraestructura sin acoplar las páginas al almacenamiento. Los datos persisten
al recargar en el mismo navegador. No se guardan contraseñas.

No existen API remota, sincronización, autenticación real, base de datos
compartida, captura de fotografías en Ionic, APK ni IPA. AWS aloja el frontend;
no respalda los registros locales ni ejecuta Django. No se garantiza el
funcionamiento offline del prototipo Ionic.

## AWS Amplify

La rama `main` está desplegada en
<https://main.d1kt5hvps8dfnb.amplifyapp.com/>.

El archivo raíz `amplify.yml` define `mobile` como raíz, `npm ci` para instalar,
`npm run build` para compilar y `dist` como salida. Las rutas internas utilizan
la reescritura hacia `/index.html` configurada en Amplify.

El cierre del 6 de septiembre de 2026 registra la implementación posterior a la
integración del PR #3 y la comprobación manual del equipo. No se necesitan
credenciales dentro del repositorio.

## Documentación técnica

- `documentation/sumativa4/CONTRATO_TECNICO.md`: contrato compartido.
- `documentation/sumativa4/PLAN_INTEGRACION.md`: planificación de referencia.
- `documentation/sumativa4/VALIDACION_BASE.md`: resultados históricos de la base;
  los resultados del cierre están indicados en la sección Validación anterior.

