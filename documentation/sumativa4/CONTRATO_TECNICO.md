# Contrato técnico de la base móvil

## Objetivo

Este documento define el contrato compartido que deben consumir los módulos
funcionales sin duplicarlo. La base usa Ionic React y TypeScript y no se
comunica con Django.

## Estructura

```text
mobile/src/
├── app/              navegación y composición principal
├── domain/           modelo e interfaz del repositorio
├── infrastructure/   persistencia local
├── state/            proveedor y hook común
├── shared/           componentes, rutas y validaciones
├── features/capture/ captura y borradores
├── features/history/ histórico y detalle
└── theme/            identidad visual común
```

## Rutas

| Ruta | Propósito | Estado en la base |
|---|---|---|
| `/login` | Acceso demostrativo | Implementado |
| `/inicio` | Resumen y accesos | Implementado |
| `/nueva` | Nueva captura | En integración |
| `/borradores` | Listado de borradores | En integración |
| `/borradores/:id` | Edición y finalización | En integración |
| `/historico` | Filtros y listado | En integración |
| `/historico/:id` | Detalle registrado | En integración |

Todas las rutas salvo `/login` están protegidas por una sesión demostrativa.

## Modelo `Novedad`

| Campo | Significado |
|---|---|
| `id` | Identificador estable generado al crear |
| `titulo` | Nombre breve del registro |
| `descripcion` | Relato inicial de la novedad |
| `disciplina` | Clasificación ficticia |
| `tipo` | Tipo de novedad |
| `turno` | Turno informado |
| `prioridad` | `baja`, `media` o `alta` |
| `estado` | Estado local del registro |
| `fechaOcurrencia` | Momento informado por el usuario |
| `fechaCreacion` | Creación local automática |
| `fechaActualizacion` | Última modificación local |
| `fechaFinalizacion` | Momento en que pasa a pendiente |

Estados:

- `borrador`: se puede actualizar y eliminar;
- `pendiente`: registro finalizado localmente;
- `en_revision`: reservado para una etapa posterior;
- `cerrada`: reservado para una etapa posterior.

Ningún estado significa que el registro esté sincronizado con un servidor.

## Métodos disponibles en `useNovedades`

```text
novedades
borradores
finalizadas
obtenerPorId(id)
guardarBorrador(datos)
actualizarBorrador(id, datos)
finalizar(id, datos)
eliminarBorrador(id)
reiniciarDemostracion()
```

El hook delega en `NovedadRepository`. Las páginas no deben acceder directamente
a `localStorage`.

## Reglas actuales

- Un borrador necesita una descripción no vacía.
- Al finalizar se exigen título, descripción, disciplina, tipo, turno y prioridad.
- Los textos se guardan sin espacios extremos.
- Actualizar conserva el identificador y no crea duplicados.
- Finalizar cambia el estado a `pendiente` y agrega fecha de finalización.
- Solo un borrador puede eliminarse.
- La contraseña demostrativa nunca se persiste.

## Persistencia

- Clave: `bitaturno:novedades:v1`.
- Formato: arreglo JSON de novedades.
- Los datos sobreviven a una recarga del navegador.
- Las semillas se crean únicamente si la clave todavía no existe.
- `reiniciarDemostracion()` restaura exactamente las semillas ficticias.
- Una estructura futura incompatible debe utilizar una clave nueva o una
  migración explícita; no se debe cambiar silenciosamente el significado de `v1`.

La sesión usa `bitaturno:demo-session:v1` en `sessionStorage` y solo almacena el
nombre ficticio. No almacena la contraseña.

## Archivos de propiedad común

No modificar sin coordinación:

```text
mobile/src/app/**
mobile/src/domain/**
mobile/src/infrastructure/**
mobile/src/state/**
mobile/src/shared/**
mobile/src/theme/**
mobile/package.json
mobile/package-lock.json
mobile/vite.config.ts
```

Los cambios en `mobile/src/features/capture/**` y
`mobile/src/features/history/**` deben respetar este contrato común.

## Solicitud de un cambio común

1. Describir en el PR qué contrato impide completar el módulo.
2. Proponer el cambio mínimo y sus efectos en los demás módulos.
3. Solicitar revisión antes de editar el archivo compartido.
4. Incorporar o actualizar una prueba del contrato.
5. Ejecutar lint, pruebas y build.
6. Registrar el acuerdo en el PR; no coordinarlo solo de forma verbal.

## Datos de demostración

Usar exclusivamente ejemplos como `usuario.demo`, `Disciplina Alfa`, `Zona 1`
y `EQ-001`. El botón **Restablecer datos ficticios** del Inicio recupera la
semilla conocida. No subir capturas, credenciales ni registros reales.
