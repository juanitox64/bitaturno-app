FORMATO_NOMBRE = "bitaturno-transfer"
FORMATO_VERSION = "1.0"

SECCION_CATALOGOS = "catalogos"
SECCION_USUARIOS = "usuarios"
SECCION_BORRADORES = "borradores"
SECCION_REGISTRADAS = "novedades_registradas"
SECCION_EVIDENCIAS = "evidencias"

SECCIONES_DATOS = (
    SECCION_CATALOGOS,
    SECCION_USUARIOS,
    SECCION_BORRADORES,
    SECCION_REGISTRADAS,
)
SECCIONES_TODAS = SECCIONES_DATOS + (SECCION_EVIDENCIAS,)

ARCHIVOS_SECCION = {
    SECCION_CATALOGOS: "data/catalogos.json",
    SECCION_USUARIOS: "data/usuarios.json",
    SECCION_BORRADORES: "data/borradores.json",
    SECCION_REGISTRADAS: "data/novedades_registradas.json",
}

EXTENSIONES_IMAGEN = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}

