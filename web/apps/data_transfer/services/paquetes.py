import hashlib
import json
import stat
import warnings
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path, PurePosixPath
from uuid import UUID

from django.conf import settings
from PIL import Image

from .constantes import (
    ARCHIVOS_SECCION,
    EXTENSIONES_IMAGEN,
    FORMATO_NOMBRE,
    FORMATO_VERSION,
    SECCION_BORRADORES,
    SECCION_CATALOGOS,
    SECCION_EVIDENCIAS,
    SECCION_REGISTRADAS,
    SECCION_USUARIOS,
    SECCIONES_DATOS,
    SECCIONES_TODAS,
)
from .excepciones import PaqueteInvalido


ARCHIVOS_RAIZ = {"manifest.json", "checksums.json", "README.txt"}
MAXIMO_JSON_BYTES = 32 * 1024 * 1024
MAXIMO_IMAGEN_BYTES = 25 * 1024 * 1024
MAXIMO_PIXELES = 50_000_000
MAXIMA_RELACION_COMPRESION = 100


@dataclass(frozen=True)
class InspeccionPaquete:
    ruta: Path
    manifest: dict
    secciones: tuple[str, ...]
    conteos: dict
    sha256: str
    tamano: int
    datos: dict


def sha256_bytes(contenido):
    return hashlib.sha256(contenido).hexdigest()


def sha256_archivo(ruta):
    resumen = hashlib.sha256()
    with Path(ruta).open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            resumen.update(bloque)
    return resumen.hexdigest()


def _leer_limitado(archivo_zip, info, limite):
    if info.file_size > limite:
        raise PaqueteInvalido(
            f"El archivo {info.filename} supera el máximo permitido."
        )
    with archivo_zip.open(info, "r") as miembro:
        contenido = miembro.read(limite + 1)
    if len(contenido) > limite:
        raise PaqueteInvalido(
            f"El archivo {info.filename} supera el máximo permitido."
        )
    return contenido


def _nombre_seguro(info):
    nombre = info.filename
    if not nombre or "\x00" in nombre or "\\" in nombre:
        raise PaqueteInvalido("El paquete contiene una ruta no válida.")
    ruta = PurePosixPath(nombre)
    if ruta.is_absolute() or ".." in ruta.parts:
        raise PaqueteInvalido(f"Ruta insegura en el paquete: {nombre}")
    if ruta.parts and ":" in ruta.parts[0]:
        raise PaqueteInvalido(f"Ruta absoluta no permitida: {nombre}")

    modo = info.external_attr >> 16
    if modo and stat.S_ISLNK(modo):
        raise PaqueteInvalido(f"No se permiten enlaces simbólicos: {nombre}")
    if modo and modo & 0o111 and not info.is_dir():
        raise PaqueteInvalido(f"No se permiten archivos ejecutables: {nombre}")
    if info.flag_bits & 0x1:
        raise PaqueteInvalido("No se permiten archivos ZIP cifrados.")

    if info.compress_size == 0 and info.file_size:
        raise PaqueteInvalido(f"Compresión sospechosa en {nombre}.")
    if info.compress_size and info.file_size / info.compress_size > MAXIMA_RELACION_COMPRESION:
        raise PaqueteInvalido(f"Relación de compresión insegura en {nombre}.")

    if info.is_dir():
        return
    if nombre in ARCHIVOS_RAIZ:
        return
    if nombre in ARCHIVOS_SECCION.values():
        return
    if ruta.parts and ruta.parts[0] == "evidencias" and len(ruta.parts) == 2:
        try:
            UUID(ruta.stem)
        except (ValueError, AttributeError) as error:
            raise PaqueteInvalido(
                f"Nombre de evidencia no portable: {nombre}"
            ) from error
        if ruta.suffix.lower() in EXTENSIONES_IMAGEN:
            return
    raise PaqueteInvalido(f"Archivo no permitido en el paquete: {nombre}")


def _cargar_json(archivo_zip, mapa, nombre, limite=MAXIMO_JSON_BYTES):
    if nombre not in mapa:
        raise PaqueteInvalido(f"Falta el archivo obligatorio {nombre}.")
    contenido = _leer_limitado(archivo_zip, mapa[nombre], limite)
    try:
        return json.loads(contenido.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PaqueteInvalido(f"JSON inválido en {nombre}.") from error


def _uuid(valor, etiqueta):
    try:
        return str(UUID(str(valor)))
    except (ValueError, TypeError, AttributeError) as error:
        raise PaqueteInvalido(f"{etiqueta} no contiene un UUID válido.") from error


def _texto(valor, etiqueta, obligatorio=True, maximo=None):
    if not isinstance(valor, str):
        raise PaqueteInvalido(f"{etiqueta} debe ser texto.")
    if obligatorio and not valor.strip():
        raise PaqueteInvalido(f"{etiqueta} es obligatorio.")
    if maximo and len(valor) > maximo:
        raise PaqueteInvalido(f"{etiqueta} supera {maximo} caracteres.")
    return valor


def _validar_catalogos(datos):
    if not isinstance(datos, dict):
        raise PaqueteInvalido("La sección de catálogos debe ser un objeto.")
    claves = {"disciplinas", "tipos_novedad", "turnos", "areas", "equipos"}
    if set(datos) != claves:
        raise PaqueteInvalido("La sección de catálogos está incompleta.")
    vistos_globales = set()
    total = 0
    for nombre, registros in datos.items():
        if not isinstance(registros, list):
            raise PaqueteInvalido(f"El catálogo {nombre} debe ser una lista.")
        vistos = set()
        for indice, registro in enumerate(registros):
            if not isinstance(registro, dict):
                raise PaqueteInvalido(f"Registro inválido en {nombre}.")
            portable_id = _uuid(
                registro.get("portable_id"),
                f"{nombre}[{indice}].portable_id",
            )
            if portable_id in vistos or portable_id in vistos_globales:
                raise PaqueteInvalido("Hay UUID duplicados en los catálogos.")
            vistos.add(portable_id)
            vistos_globales.add(portable_id)
            campo = "codigo" if nombre == "equipos" else "nombre"
            _texto(registro.get(campo), f"{nombre}[{indice}].{campo}", maximo=100)
            if not isinstance(registro.get("activo"), bool):
                raise PaqueteInvalido(f"{nombre}[{indice}].activo debe ser booleano.")
            total += 1
    return total


def _validar_usuarios(datos):
    if not isinstance(datos, list):
        raise PaqueteInvalido("La sección de usuarios debe ser una lista.")
    vistos = set()
    for indice, registro in enumerate(datos):
        if not isinstance(registro, dict) or set(registro) != {"username"}:
            raise PaqueteInvalido(
                "Cada usuario debe contener únicamente el campo username."
            )
        username = _texto(
            registro["username"],
            f"usuarios[{indice}].username",
            maximo=150,
        )
        if username in vistos:
            raise PaqueteInvalido("Hay nombres de usuario duplicados.")
        vistos.add(username)
    return len(datos)


def _validar_novedades(datos, estado_esperado, mapa, archivo_zip):
    if not isinstance(datos, list):
        raise PaqueteInvalido("La sección de novedades debe ser una lista.")
    vistos = set()
    for indice, registro in enumerate(datos):
        if not isinstance(registro, dict):
            raise PaqueteInvalido("La novedad debe representarse como un objeto.")
        portable_id = _uuid(
            registro.get("portable_id"),
            f"novedades[{indice}].portable_id",
        )
        if portable_id in vistos:
            raise PaqueteInvalido("Hay UUID de novedades duplicados.")
        vistos.add(portable_id)
        _texto(
            registro.get("creado_por"),
            f"novedades[{indice}].creado_por",
            maximo=150,
        )
        _texto(
            registro.get("titulo", ""),
            f"novedades[{indice}].titulo",
            obligatorio=False,
            maximo=180,
        )
        _texto(
            registro.get("descripcion_inicial", ""),
            f"novedades[{indice}].descripcion_inicial",
            obligatorio=False,
        )
        if registro.get("estado_registro") != estado_esperado:
            raise PaqueteInvalido("Una novedad está en una sección incorrecta.")
        for referencia in (
            "disciplina",
            "tipo_novedad",
            "turno",
            "area",
            "equipo",
        ):
            valor = registro.get(referencia)
            if valor is not None:
                _uuid(valor, f"novedades[{indice}].{referencia}")
        foto = registro.get("fotografia")
        if foto is not None:
            if not isinstance(foto, dict) or not isinstance(
                foto.get("incluida"), bool
            ):
                raise PaqueteInvalido("Metadatos de fotografía inválidos.")
            if foto["incluida"]:
                ruta = foto.get("ruta")
                _texto(ruta, "fotografia.ruta")
                if ruta not in mapa:
                    raise PaqueteInvalido(
                        f"La evidencia declarada no existe: {ruta}"
                    )
                if foto.get("sha256") != sha256_bytes(
                    _leer_limitado(
                        archivo_zip=archivo_zip,
                        info=mapa[ruta],
                        limite=MAXIMO_IMAGEN_BYTES,
                    )
                ):
                    raise PaqueteInvalido(
                        f"La evidencia declarada no coincide: {ruta}"
                    )
    return len(datos)


def _validar_imagen(archivo_zip, info):
    contenido = _leer_limitado(archivo_zip, info, MAXIMO_IMAGEN_BYTES)
    extension = PurePosixPath(info.filename).suffix.lower()
    formato_esperado = EXTENSIONES_IMAGEN[extension]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(contenido)) as imagen:
                if imagen.width * imagen.height > MAXIMO_PIXELES:
                    raise PaqueteInvalido(
                        f"La evidencia {info.filename} excede el máximo de píxeles."
                    )
                if imagen.format != formato_esperado:
                    raise PaqueteInvalido(
                        f"El contenido no coincide con la extensión de {info.filename}."
                    )
                imagen.verify()
    except PaqueteInvalido:
        raise
    except Exception as error:
        raise PaqueteInvalido(
            f"La evidencia {info.filename} no es una imagen válida."
        ) from error
    return contenido


def inspeccionar_paquete(ruta):
    ruta = Path(ruta)
    if not ruta.is_file():
        raise PaqueteInvalido("El paquete no existe.")
    tamano = ruta.stat().st_size
    if tamano <= 0 or tamano > settings.DATA_TRANSFER_MAX_PACKAGE_BYTES:
        raise PaqueteInvalido("El paquete supera el tamaño permitido.")
    if not zipfile.is_zipfile(ruta):
        raise PaqueteInvalido("El archivo no es un ZIP válido.")

    try:
        archivo_zip = zipfile.ZipFile(ruta, "r")
    except (OSError, zipfile.BadZipFile) as error:
        raise PaqueteInvalido("No fue posible abrir el paquete ZIP.") from error

    with archivo_zip:
        miembros = archivo_zip.infolist()
        archivos = [info for info in miembros if not info.is_dir()]
        if len(archivos) > settings.DATA_TRANSFER_MAX_FILES:
            raise PaqueteInvalido("El paquete contiene demasiados archivos.")
        total_descomprimido = sum(info.file_size for info in archivos)
        if total_descomprimido > settings.DATA_TRANSFER_MAX_UNCOMPRESSED_BYTES:
            raise PaqueteInvalido("El paquete se expande por sobre el máximo seguro.")

        nombres_minuscula = set()
        mapa = {}
        for info in miembros:
            _nombre_seguro(info)
            normalizado = info.filename.casefold()
            if normalizado in nombres_minuscula:
                raise PaqueteInvalido("El paquete contiene rutas duplicadas.")
            nombres_minuscula.add(normalizado)
            if not info.is_dir():
                mapa[info.filename] = info

        manifest = _cargar_json(
            archivo_zip,
            mapa,
            "manifest.json",
            limite=1024 * 1024,
        )
        checksums = _cargar_json(
            archivo_zip,
            mapa,
            "checksums.json",
            limite=1024 * 1024,
        )
        if not isinstance(manifest, dict):
            raise PaqueteInvalido("El manifiesto debe ser un objeto.")
        if manifest.get("formato") != FORMATO_NOMBRE:
            raise PaqueteInvalido("El paquete no pertenece a BitaTurno.")
        if manifest.get("version") != FORMATO_VERSION:
            raise PaqueteInvalido("La versión del paquete no es compatible.")

        secciones = manifest.get("secciones")
        if (
            not isinstance(secciones, list)
            or not secciones
            or len(secciones) != len(set(secciones))
            or any(seccion not in SECCIONES_TODAS for seccion in secciones)
        ):
            raise PaqueteInvalido("El manifiesto declara secciones inválidas.")

        if not isinstance(checksums, dict):
            raise PaqueteInvalido("El archivo de checksums debe ser un objeto.")
        esperados = set(mapa) - {"checksums.json"}
        if set(checksums) != esperados:
            raise PaqueteInvalido("La lista de checksums no cubre exactamente el paquete.")
        for nombre, esperado in checksums.items():
            if not isinstance(esperado, str) or len(esperado) != 64:
                raise PaqueteInvalido(f"Checksum inválido para {nombre}.")
            contenido = _leer_limitado(
                archivo_zip,
                mapa[nombre],
                settings.DATA_TRANSFER_MAX_UNCOMPRESSED_BYTES,
            )
            if sha256_bytes(contenido) != esperado:
                raise PaqueteInvalido(f"Falló la integridad de {nombre}.")

        datos = {}
        conteos = {}
        for seccion in SECCIONES_DATOS:
            archivo = ARCHIVOS_SECCION[seccion]
            if seccion in secciones:
                datos[seccion] = _cargar_json(archivo_zip, mapa, archivo)
            elif archivo in mapa:
                raise PaqueteInvalido(
                    f"El archivo {archivo} no fue declarado en el manifiesto."
                )

        if SECCION_CATALOGOS in datos:
            conteos[SECCION_CATALOGOS] = _validar_catalogos(
                datos[SECCION_CATALOGOS]
            )
        if SECCION_USUARIOS in datos:
            conteos[SECCION_USUARIOS] = _validar_usuarios(
                datos[SECCION_USUARIOS]
            )

        if SECCION_BORRADORES in datos:
            conteos[SECCION_BORRADORES] = _validar_novedades(
                datos[SECCION_BORRADORES],
                "BORRADOR",
                mapa,
                archivo_zip,
            )
        if SECCION_REGISTRADAS in datos:
            conteos[SECCION_REGISTRADAS] = _validar_novedades(
                datos[SECCION_REGISTRADAS],
                "REGISTRADA",
                mapa,
                archivo_zip,
            )

        evidencias = [
            info
            for nombre, info in mapa.items()
            if nombre.startswith("evidencias/")
        ]
        if evidencias and SECCION_EVIDENCIAS not in secciones:
            raise PaqueteInvalido(
                "El paquete contiene evidencias no declaradas."
            )
        for info in evidencias:
            _validar_imagen(archivo_zip, info)
        if SECCION_EVIDENCIAS in secciones:
            conteos[SECCION_EVIDENCIAS] = len(evidencias)

        declarados = manifest.get("conteos")
        if not isinstance(declarados, dict):
            raise PaqueteInvalido("El manifiesto no contiene conteos válidos.")
        for seccion in secciones:
            if declarados.get(seccion) != conteos.get(seccion, 0):
                raise PaqueteInvalido(
                    f"El conteo de {seccion} no coincide con el contenido."
                )

    return InspeccionPaquete(
        ruta=ruta,
        manifest=manifest,
        secciones=tuple(secciones),
        conteos=conteos,
        sha256=sha256_archivo(ruta),
        tamano=tamano,
        datos=datos,
    )


def leer_evidencia_validada(ruta_paquete, ruta_evidencia):
    inspeccionar_paquete(ruta_paquete)
    with zipfile.ZipFile(ruta_paquete, "r") as archivo_zip:
        try:
            info = archivo_zip.getinfo(ruta_evidencia)
        except KeyError as error:
            raise PaqueteInvalido("La evidencia solicitada no existe.") from error
        return _validar_imagen(archivo_zip, info)
