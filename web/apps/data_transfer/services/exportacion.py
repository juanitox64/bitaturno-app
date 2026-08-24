import json
import os
import zipfile
from pathlib import Path, PurePosixPath
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.utils import timezone

from apps.bitaturno.models import (
    Area,
    Disciplina,
    Equipo,
    Novedad,
    TipoNovedad,
    Turno,
)

from .constantes import (
    ARCHIVOS_SECCION,
    FORMATO_NOMBRE,
    FORMATO_VERSION,
    SECCION_BORRADORES,
    SECCION_CATALOGOS,
    SECCION_EVIDENCIAS,
    SECCION_REGISTRADAS,
    SECCION_USUARIOS,
    SECCIONES_DATOS,
)
from .excepciones import ErrorTransferencia
from .paquetes import (
    MAXIMO_IMAGEN_BYTES,
    inspeccionar_paquete,
    sha256_bytes,
)


CATALOGOS = (
    ("disciplinas", Disciplina, "nombre"),
    ("tipos_novedad", TipoNovedad, "nombre"),
    ("turnos", Turno, "nombre"),
    ("areas", Area, "nombre"),
    ("equipos", Equipo, "codigo"),
)


def _fecha(valor):
    return valor.isoformat() if valor else None


def _version_aplicacion():
    ruta = Path(settings.BASE_DIR) / "VERSION"
    try:
        return ruta.read_text(encoding="utf-8").strip() or "0.1"
    except OSError:
        return "0.1"


def _serializar_catalogos():
    resultado = {}
    for nombre, modelo, campo in CATALOGOS:
        resultado[nombre] = [
            {
                "portable_id": str(objeto.portable_id),
                campo: getattr(objeto, campo),
                "activo": objeto.activo,
                "fecha_creacion": _fecha(objeto.fecha_creacion),
                "fecha_actualizacion": _fecha(objeto.fecha_actualizacion),
            }
            for objeto in modelo.objects.order_by("pk")
        ]
    return resultado


def _serializar_usuarios():
    Usuario = get_user_model()
    return [
        {"username": username}
        for username in Usuario.objects.order_by("username").values_list(
            "username",
            flat=True,
        )
    ]


def _leer_evidencia(nombre):
    try:
        with default_storage.open(nombre, "rb") as archivo:
            contenido = archivo.read(MAXIMO_IMAGEN_BYTES + 1)
    except (OSError, FileNotFoundError) as error:
        raise ErrorTransferencia(
            f"No fue posible leer una evidencia asociada a {nombre}."
        ) from error
    if len(contenido) > MAXIMO_IMAGEN_BYTES:
        raise ErrorTransferencia(
            f"La evidencia {nombre} supera el máximo portable de 25 MB."
        )
    return contenido


def _serializar_novedades(estado, incluir_evidencias, archivos):
    resultado = []
    consulta = (
        Novedad.objects.filter(estado_registro=estado)
        .select_related(
            "disciplina",
            "tipo_novedad",
            "turno",
            "area",
            "equipo",
            "creado_por",
        )
        .order_by("pk")
    )
    for novedad in consulta:
        fotografia = None
        if novedad.fotografia:
            fotografia = {"incluida": False}
            if incluir_evidencias:
                extension = PurePosixPath(novedad.fotografia.name).suffix.lower()
                if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
                    raise ErrorTransferencia(
                        "Una evidencia existente tiene una extensión no portable."
                    )
                contenido = _leer_evidencia(novedad.fotografia.name)
                ruta = f"evidencias/{novedad.portable_id}{extension}"
                archivos[ruta] = contenido
                fotografia = {
                    "incluida": True,
                    "ruta": ruta,
                    "sha256": sha256_bytes(contenido),
                }

        resultado.append(
            {
                "portable_id": str(novedad.portable_id),
                "titulo": novedad.titulo,
                "descripcion_inicial": novedad.descripcion_inicial,
                "disciplina": (
                    str(novedad.disciplina.portable_id)
                    if novedad.disciplina
                    else None
                ),
                "tipo_novedad": (
                    str(novedad.tipo_novedad.portable_id)
                    if novedad.tipo_novedad
                    else None
                ),
                "turno": (
                    str(novedad.turno.portable_id) if novedad.turno else None
                ),
                "area": str(novedad.area.portable_id) if novedad.area else None,
                "equipo": (
                    str(novedad.equipo.portable_id) if novedad.equipo else None
                ),
                "prioridad": novedad.prioridad,
                "estado_registro": novedad.estado_registro,
                "estado_operacional": novedad.estado_operacional,
                "fecha_ocurrencia": _fecha(novedad.fecha_ocurrencia),
                "fecha_captura": _fecha(novedad.fecha_captura),
                "fecha_actualizacion": _fecha(novedad.fecha_actualizacion),
                "fecha_finalizacion": _fecha(novedad.fecha_finalizacion),
                "fecha_cierre": _fecha(novedad.fecha_cierre),
                "fotografia": fotografia,
                "creado_por": novedad.creado_por.username,
            }
        )
    return resultado


def _json_bytes(valor):
    return json.dumps(
        valor,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ).encode("utf-8")


def _limpiar_retencion(directorio):
    limite = max(1, settings.DATA_TRANSFER_RETENTION)
    paquetes = sorted(
        directorio.glob("*.zip"),
        key=lambda ruta: ruta.stat().st_mtime,
        reverse=True,
    )
    for antiguo in paquetes[limite:]:
        antiguo.unlink(missing_ok=True)


def crear_paquete_exportacion(
    ruta_salida,
    secciones,
    incluir_evidencias=False,
    limpiar_retencion=False,
):
    secciones = tuple(
        seccion for seccion in SECCIONES_DATOS if seccion in set(secciones)
    )
    if not secciones:
        raise ErrorTransferencia("Seleccione al menos una sección para exportar.")
    if incluir_evidencias and not {
        SECCION_BORRADORES,
        SECCION_REGISTRADAS,
    }.intersection(secciones):
        raise ErrorTransferencia(
            "Las evidencias requieren exportar borradores o novedades registradas."
        )

    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    if ruta_salida.exists():
        raise ErrorTransferencia("El archivo de salida ya existe.")
    ruta_temporal = ruta_salida.parent / f".{ruta_salida.name}.{uuid4().hex}.tmp"

    archivos = {}
    conteos = {}
    if SECCION_CATALOGOS in secciones:
        datos = _serializar_catalogos()
        archivos[ARCHIVOS_SECCION[SECCION_CATALOGOS]] = _json_bytes(datos)
        conteos[SECCION_CATALOGOS] = sum(len(registros) for registros in datos.values())
    if SECCION_USUARIOS in secciones:
        datos = _serializar_usuarios()
        archivos[ARCHIVOS_SECCION[SECCION_USUARIOS]] = _json_bytes(datos)
        conteos[SECCION_USUARIOS] = len(datos)
    if SECCION_BORRADORES in secciones:
        datos = _serializar_novedades(
            Novedad.EstadoRegistro.BORRADOR,
            incluir_evidencias,
            archivos,
        )
        archivos[ARCHIVOS_SECCION[SECCION_BORRADORES]] = _json_bytes(datos)
        conteos[SECCION_BORRADORES] = len(datos)
    if SECCION_REGISTRADAS in secciones:
        datos = _serializar_novedades(
            Novedad.EstadoRegistro.REGISTRADA,
            incluir_evidencias,
            archivos,
        )
        archivos[ARCHIVOS_SECCION[SECCION_REGISTRADAS]] = _json_bytes(datos)
        conteos[SECCION_REGISTRADAS] = len(datos)

    secciones_manifest = list(secciones)
    if incluir_evidencias:
        secciones_manifest.append(SECCION_EVIDENCIAS)
        conteos[SECCION_EVIDENCIAS] = sum(
            1 for nombre in archivos if nombre.startswith("evidencias/")
        )

    readme = (
        "Paquete lógico de BitaTurno.\n"
        "No contiene contraseñas, hashes, privilegios ni permisos de usuarios.\n"
        "Valide y simule la importación antes de confirmar cualquier cambio.\n"
    ).encode("utf-8")
    archivos["README.txt"] = readme
    manifest = {
        "formato": FORMATO_NOMBRE,
        "version": FORMATO_VERSION,
        "version_aplicacion": _version_aplicacion(),
        "creado_en": timezone.now().isoformat(),
        "secciones": secciones_manifest,
        "conteos": conteos,
        "incluye_credenciales": False,
    }
    archivos["manifest.json"] = _json_bytes(manifest)
    checksums = {
        nombre: sha256_bytes(contenido)
        for nombre, contenido in sorted(archivos.items())
    }
    archivos["checksums.json"] = _json_bytes(checksums)

    try:
        with zipfile.ZipFile(
            ruta_temporal,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
            allowZip64=False,
        ) as archivo_zip:
            for nombre, contenido in sorted(archivos.items()):
                archivo_zip.writestr(nombre, contenido)
        if ruta_temporal.stat().st_size > settings.DATA_TRANSFER_MAX_PACKAGE_BYTES:
            raise ErrorTransferencia("El paquete generado supera el máximo permitido.")
        os.replace(ruta_temporal, ruta_salida)
        inspeccion = inspeccionar_paquete(ruta_salida)
    except Exception:
        ruta_temporal.unlink(missing_ok=True)
        ruta_salida.unlink(missing_ok=True)
        raise

    if limpiar_retencion:
        _limpiar_retencion(ruta_salida.parent)
    return inspeccion

