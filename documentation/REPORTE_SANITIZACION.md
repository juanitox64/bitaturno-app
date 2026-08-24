# Reporte de sanitización

## Origen

La copia pública se construyó desde el paquete local reproducible y verificado
de BitaTurno. No se inicializó Git en la carpeta operativa ni se reutilizó un
historial anterior.

## Elementos incluidos

- código fuente Django;
- migraciones;
- pruebas automatizadas;
- plantillas y archivos estáticos;
- dependencias declaradas;
- documentación académica;
- datos ficticios del mockup.

## Elementos excluidos

- bases de datos;
- entornos virtuales y cachés;
- fotografías y archivos cargados;
- usuarios y credenciales;
- exportaciones, importaciones y respaldos con datos;
- registros de ejecución;
- certificados, claves y tokens;
- configuración de infraestructura privada;
- documentación histórica con resultados de testers;
- direcciones privadas o internas.

## Ajuste preventivo

La copia pública no contiene una clave Django fija. En modo de desarrollo genera
una clave efímera; con `DJANGO_DEBUG=0` exige `DJANGO_SECRET_KEY` mediante el
entorno.

## Comprobaciones realizadas antes de publicar

- revisión de nombres de archivos versionados;
- búsqueda de firmas habituales de tokens y claves privadas;
- búsqueda de cuentas, correos, direcciones y nombres operacionales;
- confirmación de que `.gitignore` excluye datos y credenciales;
- ejecución del MVP con una base temporal vacía;
- eliminación de cachés generadas durante las pruebas.

Las coincidencias correspondientes a nombres de variables, valores ficticios o
integrantes exigidos por la evaluación se revisan por contexto. Este reporte no
reproduce ningún valor sensible detectado.

## Resultado inicial

La revisión inicial no encontró datos operacionales ni secretos reales dentro
de los archivos preparados para el repositorio. Se repetirá la comprobación
sobre la lista completa de archivos antes del cierre.
