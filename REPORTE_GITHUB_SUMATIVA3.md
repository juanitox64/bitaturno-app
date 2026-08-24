# Reporte GitHub — BitaTurno Sumativa 3

## 1. Cuenta utilizada

`juanitox64`, autenticada mediante GitHub CLI. Los commits usan la dirección
`noreply` de GitHub para no publicar el correo personal configurado globalmente.

## 2. Repositorio

- Nombre: `bitaturno-app`
- URL: <https://github.com/juanitox64/bitaturno-app>
- Visibilidad: **PUBLIC**
- Rama predeterminada: `main`
- Descripción y URL de Pages configuradas.

## 3. Primer commit

```text
SHA: a5abcaa9ee742972d3ab31f9b1b7a7c6d630ee93
Mensaje: chore: crear estructura inicial de BitaTurno
```

El primer commit contiene únicamente README inicial, exclusiones, ejemplo de
entorno y estructura de carpetas. No fue reescrito después de publicarse.

## 4. Historial resumido

Al cerrar la entrega existen 11 commits coherentes, incluido este reporte:

```text
chore: crear estructura inicial de BitaTurno
feat: incorporar MVP web sanitizado
feat: agregar mockup movil navegable
docs: documentar integracion movil web
ci: agregar pruebas y despliegue de GitHub Pages
fix: corregir rutas temporales de CI
ci: actualizar acciones oficiales
fix: ocultar navegacion antes del ingreso
test: verificar navegacion y funcionamiento publico
fix: actualizar cache del mockup publicado
docs: agregar evidencias y enlaces finales
```

No se utilizó `force push` ni se reescribió el historial.

## 5. GitHub Pages

- URL: <https://juanitox64.github.io/bitaturno-app/>
- Fuente: workflow de GitHub Actions.
- Carpeta publicada: `docs/`.
- HTTPS: forzado.
- Estado comprobado: **success**.
- Recursos públicos comprobados: 9/9 con HTTP 200.

## 6. Integración continua

El workflow usa Python 3.11 y versiones oficiales actuales de las acciones.
Ejecuta migraciones, `check`, 57 pruebas Django, 9 pruebas del mockup y la
comprobación de migraciones pendientes.

La primera ejecución registró una falla de evaluación en las rutas temporales.
Se corrigió sin borrar el historial. Las ejecuciones posteriores aprobaron; la
ejecución funcional de referencia es la 32693419867.

## 7. Resultado del MVP

```text
check: System check identified no issues (0 silenced).
makemigrations --check --dry-run: No changes detected
migrate desde base vacía: OK
pruebas: 57/57 OK
```

El clon limpio ejecutó el MVP temporalmente y respondió HTTP 200.

## 8. Resultado del mockup

- Siete pantallas presentes.
- Navegación principal completa.
- Validación de captura y finalización.
- Simulación visual de conectividad y sincronización.
- Resumen redactado manualmente.
- Histórico, filtros y detalle.
- Diseño comprobado en 390 × 844 y escritorio.
- Consola: cero errores y cero advertencias.
- Nueve pruebas estructurales: `OK`.

## 9. Pantallas creadas

1. Inicio de sesión.
2. Mi jornada.
3. Nueva captura.
4. Mis borradores.
5. Completar novedad.
6. Resumen de jornada.
7. Histórico y detalle.

## 10. Evidencias

Directorio: `documentation/evidencias/`.

- `repositorio-publico.png`
- `primer-commit.png`
- `github-actions.png`
- `pages-inicio-movil.png`
- `pages-captura-movil.png`
- `pages-resumen-movil.png`
- `pages-flujo-completo.png`

Todas utilizan datos ficticios y fueron revisadas visualmente.

## 11. Clon limpio

Se creó un entorno virtual nuevo desde el repositorio público, se instalaron las
dependencias fijadas, se migró una base nueva, se ejecutaron 66 pruebas en total
y se iniciaron temporalmente el MVP y el mockup.

```text
57 pruebas Django: OK
9 pruebas del mockup: OK
MVP: HTTP 200
Mockup: HTTP 200
Carpeta temporal: eliminada
```

## 12. Sanitización

Se excluyeron bases, fotografías, usuarios operacionales, contraseñas,
credenciales, exportaciones, respaldos con datos, registros, cachés, entornos
virtuales y configuración de infraestructura privada.

La revisión de firmas de secretos, nombres de archivos, cuentas, correos y
direcciones no encontró valores privados en los archivos versionados. La copia
pública genera una clave Django efímera en desarrollo y exige configuración por
entorno cuando el modo de depuración está desactivado.

## 13. Funciones implementadas

- MVP Django con autenticación y administración.
- CRUD, borradores y finalización.
- Fotografías, histórico, filtros y estados.
- Permisos, confirmación de eliminación y contadores.
- Migraciones y pruebas automatizadas.
- Mockup estático navegable.
- CI y publicación Pages.

## 14. Funciones representadas

- jornada móvil;
- captura local sin cobertura;
- cola y estados de sincronización;
- integración por API;
- resumen móvil de jornada.

Estas funciones no se presentan como capacidades del backend actual.

## 15. Limitaciones

- No existe aplicación móvil nativa.
- No existe API REST ni sincronización real.
- Las capturas del mockup se reinician al recargar.
- La caché PWA corresponde solo al sitio estático.
- No se hizo una prueba automatizada de corte total de red.
- Los otros integrantes no fueron agregados sin sus nombres reales de GitHub.
- El MVP conserva SQLite y una fotografía por novedad.

## 16. Elementos sugeridos para el informe Word

1. URL y captura del repositorio público.
2. SHA y captura del primer commit.
3. Captura de CI aprobada.
4. URL pública del mockup.
5. Tres capturas móviles y una de escritorio.
6. Diagrama de flujo de navegación.
7. Diagrama de arquitectura propuesta.
8. Tabla que separa implementado, representado y futuro.
9. Resultado de 57 pruebas del MVP y 9 del mockup.
10. Resultado del clon limpio y limitaciones reales.

## 17. Pendientes manuales

- Incorporar las evidencias seleccionadas en el documento Word de la Sumativa 3.
- Asociar a los demás integrantes cuando entreguen sus usuarios de GitHub.
- Realizar, si la evaluación lo solicita, una revisión manual adicional desde
  los teléfonos de los integrantes.
