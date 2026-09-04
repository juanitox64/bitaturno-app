# BitaTurno móvil — base `0.4.0-rc.1`

Base híbrida académica construida con Ionic, React y TypeScript. Se ejecuta en
navegador y está organizada para que los módulos de captura e histórico puedan
desarrollarse en ramas separadas sin modificar el contrato común.

## Estado real

Implementado y probado:

- navegación Ionic para siete rutas;
- protección local básica de rutas;
- login demostrativo y cierre de sesión;
- inicio con contadores y accesos;
- modelo `Novedad` y validaciones comunes;
- repositorio `localStorage` tras una interfaz;
- datos semilla ficticios y restablecimiento;
- proveedor y hook `useNovedades`;
- pruebas de infraestructura, validaciones, Login e Inicio.

Preparado, pero todavía en integración:

- captura, borradores y finalización;
- histórico, filtros, detalle y revisión móvil.

No existen API remota, sincronización, autenticación real, almacenamiento seguro
de credenciales, APK, IPA ni despliegue AWS en esta base.

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
contraseña ficticios no vacíos. La contraseña se descarta inmediatamente y la
sesión demostrativa se conserva solo en `sessionStorage`.

## Validación

```text
npm ci
npm run lint
npm run test -- --run
npm run build
```

La salida estática se genera en `mobile/dist/`.

## Rutas

| Ruta | Estado |
|---|---|
| `/login` | Implementada |
| `/inicio` | Implementada |
| `/nueva` | Esqueleto en integración |
| `/borradores` | Esqueleto en integración |
| `/borradores/:id` | Esqueleto en integración |
| `/historico` | Esqueleto en integración |
| `/historico/:id` | Esqueleto en integración |

## Persistencia

La clave es `bitaturno:novedades:v1`. El repositorio es síncrono y está aislado
mediante `NovedadRepository`, de modo que una API futura pueda sustituir la
infraestructura sin acoplar las páginas al almacenamiento del navegador. Los
datos persisten al recargar. No se guardan contraseñas.

## AWS Amplify: pasos pendientes

El archivo raíz `amplify.yml` describe el monorepo con `mobile/` como aplicación
y `dist/` como salida. Una persona autorizada deberá:

1. ingresar a AWS Amplify;
2. seleccionar **Host web app** y conectar el repositorio autorizado;
3. escoger la rama revisada que se decida desplegar;
4. confirmar que el monorepo usa `mobile` como raíz de aplicación;
5. revisar que la configuración detectada coincida con `amplify.yml`;
6. ejecutar el despliegue y comprobar directamente todas las rutas;
7. registrar la URL y las evidencias reales solo después del resultado exitoso.

No se requieren credenciales dentro del repositorio y esta tarea no realizó el
despliegue.

## Documentación técnica

La base se documenta en:

- `documentation/sumativa4/CONTRATO_TECNICO.md`;
- `documentation/sumativa4/PLAN_INTEGRACION.md`;
- `documentation/sumativa4/VALIDACION_BASE.md`.
