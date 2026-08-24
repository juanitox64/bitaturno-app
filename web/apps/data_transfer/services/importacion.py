from collections import defaultdict
from pathlib import Path, PurePosixPath
from uuid import UUID, uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.bitaturno.models import (
    Area,
    Disciplina,
    Equipo,
    Novedad,
    TipoNovedad,
    Turno,
)

from ..models import Transferencia
from .constantes import (
    SECCION_BORRADORES,
    SECCION_CATALOGOS,
    SECCION_EVIDENCIAS,
    SECCION_REGISTRADAS,
    SECCION_USUARIOS,
    SECCIONES_DATOS,
)
from .excepciones import ConflictoImportacion, ErrorTransferencia
from .exportacion import crear_paquete_exportacion
from .paquetes import inspeccionar_paquete, leer_evidencia_validada


CATALOGOS = (
    ("disciplinas", Disciplina, "nombre"),
    ("tipos_novedad", TipoNovedad, "nombre"),
    ("turnos", Turno, "nombre"),
    ("areas", Area, "nombre"),
    ("equipos", Equipo, "codigo"),
)
REFERENCIAS = {
    "disciplina": Disciplina,
    "tipo_novedad": TipoNovedad,
    "turno": Turno,
    "area": Area,
    "equipo": Equipo,
}


def _fecha(valor, etiqueta, obligatoria=False):
    if valor in (None, ""):
        if obligatoria:
            raise ErrorTransferencia(f"Falta la fecha {etiqueta}.")
        return None
    resultado = parse_datetime(valor) if isinstance(valor, str) else None
    if resultado is None or timezone.is_naive(resultado):
        raise ErrorTransferencia(f"La fecha {etiqueta} no es válida.")
    return resultado


def _validar_politica(politica):
    if politica not in Transferencia.Politica.values:
        raise ErrorTransferencia("La política de conflictos no es válida.")


def _contador():
    return defaultdict(
        lambda: {
            "creados": 0,
            "actualizados": 0,
            "omitidos": 0,
            "preservados": 0,
        }
    )


def _resolver_existente(modelo, portable_id, campo_natural, valor_natural):
    existente = modelo.objects.filter(portable_id=portable_id).first()
    natural = modelo.objects.filter(**{campo_natural: valor_natural}).first()
    if natural and (existente is None or natural.pk != existente.pk):
        raise ConflictoImportacion(
            f"Existe un valor natural de {modelo._meta.verbose_name} "
            "con otro identificador portable."
        )
    return existente


def _aplicar_catalogos(datos, politica, conteos):
    for nombre, modelo, campo in CATALOGOS:
        for registro in datos[nombre]:
            portable_id = UUID(registro["portable_id"])
            valor = registro[campo]
            if campo == "codigo":
                valor = valor.strip().upper()
            existente = _resolver_existente(
                modelo,
                portable_id,
                campo,
                valor,
            )
            if existente and politica == Transferencia.Politica.DETENER:
                raise ConflictoImportacion(
                    f"Ya existe {modelo._meta.verbose_name} con UUID "
                    f"{portable_id}."
                )
            if existente and politica == Transferencia.Politica.OMITIR:
                conteos[SECCION_CATALOGOS]["omitidos"] += 1
                continue

            objeto = existente or modelo(portable_id=portable_id)
            setattr(objeto, campo, valor)
            objeto.activo = registro["activo"]
            try:
                objeto.full_clean()
                objeto.save()
            except (ValidationError, IntegrityError) as error:
                raise ErrorTransferencia(
                    f"No fue posible aplicar un registro de {nombre}."
                ) from error

            fechas = {
                "fecha_creacion": _fecha(
                    registro.get("fecha_creacion"),
                    f"{nombre}.fecha_creacion",
                    obligatoria=True,
                ),
                "fecha_actualizacion": _fecha(
                    registro.get("fecha_actualizacion"),
                    f"{nombre}.fecha_actualizacion",
                    obligatoria=True,
                ),
            }
            modelo.objects.filter(pk=objeto.pk).update(**fechas)
            clave = "actualizados" if existente else "creados"
            conteos[SECCION_CATALOGOS][clave] += 1


def _aplicar_usuarios(datos, politica, conteos):
    Usuario = get_user_model()
    for registro in datos:
        username = registro["username"]
        existente = Usuario.objects.filter(username=username).first()
        if existente and politica == Transferencia.Politica.DETENER:
            raise ConflictoImportacion(
                f"Ya existe el usuario {username}."
            )
        if existente:
            clave = (
                "omitidos"
                if politica == Transferencia.Politica.OMITIR
                else "preservados"
            )
            conteos[SECCION_USUARIOS][clave] += 1
            continue

        usuario = Usuario(
            username=username,
            is_active=False,
            is_staff=False,
            is_superuser=False,
        )
        usuario.set_unusable_password()
        try:
            usuario.full_clean()
            usuario.save()
        except (ValidationError, IntegrityError) as error:
            raise ErrorTransferencia(
                f"No fue posible crear el usuario {username}."
            ) from error
        conteos[SECCION_USUARIOS]["creados"] += 1


def _resolver_referencia(registro, campo):
    valor = registro.get(campo)
    if valor is None:
        return None
    modelo = REFERENCIAS[campo]
    objeto = modelo.objects.filter(portable_id=UUID(valor)).first()
    if objeto is None:
        raise ErrorTransferencia(
            f"No existe la referencia {campo} requerida por una novedad."
        )
    return objeto


def _eliminar_evidencia_si_no_compartida(nombre, novedad_pk):
    if not nombre:
        return
    if Novedad.objects.exclude(pk=novedad_pk).filter(fotografia=nombre).exists():
        return
    default_storage.delete(nombre)


def _preparar_fotografia(
    registro,
    existente,
    importar_evidencias,
    simulacion,
    ruta_paquete,
    archivos_nuevos,
    archivos_antiguos,
):
    foto = registro.get("fotografia")
    nombre_anterior = existente.fotografia.name if existente and existente.fotografia else ""
    if foto is None:
        if existente and importar_evidencias and nombre_anterior:
            archivos_antiguos.append((nombre_anterior, existente.pk))
            return ""
        return nombre_anterior
    if not foto.get("incluida") or not importar_evidencias:
        return nombre_anterior

    extension = PurePosixPath(foto["ruta"]).suffix.lower()
    if simulacion:
        return f"novedades/transferencias/simulacion-{registro['portable_id']}{extension}"

    contenido = leer_evidencia_validada(ruta_paquete, foto["ruta"])
    nombre_deseado = (
        f"novedades/transferencias/{registro['portable_id']}-"
        f"{uuid4().hex}{extension}"
    )
    nombre_nuevo = default_storage.save(nombre_deseado, ContentFile(contenido))
    archivos_nuevos.append(nombre_nuevo)
    if nombre_anterior and nombre_anterior != nombre_nuevo:
        archivos_antiguos.append((nombre_anterior, existente.pk))
    return nombre_nuevo


def _campos_novedad(
    registro,
    fotografia,
):
    return {
        "titulo": registro.get("titulo", ""),
        "descripcion_inicial": registro.get("descripcion_inicial", ""),
        "disciplina": _resolver_referencia(registro, "disciplina"),
        "tipo_novedad": _resolver_referencia(registro, "tipo_novedad"),
        "turno": _resolver_referencia(registro, "turno"),
        "area": _resolver_referencia(registro, "area"),
        "equipo": _resolver_referencia(registro, "equipo"),
        "prioridad": registro.get("prioridad", ""),
        "estado_registro": registro["estado_registro"],
        "estado_operacional": registro.get("estado_operacional", ""),
        "fecha_ocurrencia": _fecha(
            registro.get("fecha_ocurrencia"),
            "novedad.fecha_ocurrencia",
        ),
        "fecha_finalizacion": _fecha(
            registro.get("fecha_finalizacion"),
            "novedad.fecha_finalizacion",
            obligatoria=registro["estado_registro"] == "REGISTRADA",
        ),
        "fecha_cierre": _fecha(
            registro.get("fecha_cierre"),
            "novedad.fecha_cierre",
        ),
        "fotografia": fotografia,
    }


def _aplicar_novedades(
    datos,
    seccion,
    politica,
    importar_evidencias,
    simulacion,
    ruta_paquete,
    conteos,
    archivos_nuevos,
    archivos_antiguos,
):
    Usuario = get_user_model()
    for registro in datos:
        portable_id = UUID(registro["portable_id"])
        existente = Novedad.objects.filter(portable_id=portable_id).first()
        if existente and politica == Transferencia.Politica.DETENER:
            raise ConflictoImportacion(
                f"Ya existe la novedad con UUID {portable_id}."
            )
        if existente and politica == Transferencia.Politica.OMITIR:
            conteos[seccion]["omitidos"] += 1
            continue

        autor = Usuario.objects.filter(username=registro["creado_por"]).first()
        if autor is None:
            raise ErrorTransferencia(
                "No existe el usuario autor requerido por una novedad."
            )
        fotografia = _preparar_fotografia(
            registro,
            existente,
            importar_evidencias,
            simulacion,
            ruta_paquete,
            archivos_nuevos,
            archivos_antiguos,
        )
        campos = _campos_novedad(registro, fotografia)
        objeto = existente or Novedad(
            portable_id=portable_id,
            creado_por=autor,
        )
        objeto.creado_por = autor
        for nombre, valor in campos.items():
            setattr(objeto, nombre, valor)

        try:
            excluir = None
            if (
                simulacion
                and importar_evidencias
                and (registro.get("fotografia") or {}).get("incluida")
            ):
                excluir = {"fotografia"}
            objeto.full_clean(exclude=excluir)
            if existente:
                valores = {
                    f"{nombre}_id" if nombre in REFERENCIAS else nombre: (
                        valor.pk if nombre in REFERENCIAS and valor else None
                    )
                    for nombre, valor in campos.items()
                }
                valores["creado_por_id"] = autor.pk
                Novedad.objects.filter(pk=existente.pk).update(**valores)
            else:
                objeto.save()
        except (ValidationError, IntegrityError) as error:
            raise ErrorTransferencia(
                f"No fue posible aplicar la novedad {portable_id}."
            ) from error

        fechas = {
            "fecha_captura": _fecha(
                registro.get("fecha_captura"),
                "novedad.fecha_captura",
                obligatoria=True,
            ),
            "fecha_actualizacion": _fecha(
                registro.get("fecha_actualizacion"),
                "novedad.fecha_actualizacion",
                obligatoria=True,
            ),
        }
        Novedad.objects.filter(pk=objeto.pk).update(**fechas)
        clave = "actualizados" if existente else "creados"
        conteos[seccion][clave] += 1


def _crear_respaldo_previo():
    directorio = Path(settings.DATA_TRANSFER_BACKUP_ROOT)
    directorio.mkdir(parents=True, exist_ok=True)
    nombre = (
        f"respaldo-preimportacion-"
        f"{timezone.now().strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}.zip"
    )
    ruta = directorio / nombre
    crear_paquete_exportacion(
        ruta,
        secciones=SECCIONES_DATOS,
        incluir_evidencias=True,
        limpiar_retencion=True,
    )
    return ruta


def ejecutar_importacion(
    ruta_paquete,
    secciones,
    politica,
    simulacion=True,
):
    inspeccion = inspeccionar_paquete(ruta_paquete)
    _validar_politica(politica)
    secciones = tuple(dict.fromkeys(secciones))
    if not secciones:
        raise ErrorTransferencia("Seleccione al menos una sección para importar.")
    if any(seccion not in inspeccion.secciones for seccion in secciones):
        raise ErrorTransferencia(
            "Se solicitó una sección que no existe en el paquete."
        )
    if any(
        seccion not in SECCIONES_DATOS + (SECCION_EVIDENCIAS,)
        for seccion in secciones
    ):
        raise ErrorTransferencia("Una sección seleccionada no es válida.")

    importar_evidencias = SECCION_EVIDENCIAS in secciones
    if importar_evidencias and not {
        SECCION_BORRADORES,
        SECCION_REGISTRADAS,
    }.intersection(secciones):
        raise ErrorTransferencia(
            "Las evidencias deben importarse junto con sus novedades."
        )

    respaldo = None if simulacion else _crear_respaldo_previo()
    conteos = _contador()
    archivos_nuevos = []
    archivos_antiguos = []
    try:
        with transaction.atomic():
            if SECCION_CATALOGOS in secciones:
                _aplicar_catalogos(
                    inspeccion.datos[SECCION_CATALOGOS],
                    politica,
                    conteos,
                )
            if SECCION_USUARIOS in secciones:
                _aplicar_usuarios(
                    inspeccion.datos[SECCION_USUARIOS],
                    politica,
                    conteos,
                )
            if SECCION_BORRADORES in secciones:
                _aplicar_novedades(
                    inspeccion.datos[SECCION_BORRADORES],
                    SECCION_BORRADORES,
                    politica,
                    importar_evidencias,
                    simulacion,
                    ruta_paquete,
                    conteos,
                    archivos_nuevos,
                    archivos_antiguos,
                )
            if SECCION_REGISTRADAS in secciones:
                _aplicar_novedades(
                    inspeccion.datos[SECCION_REGISTRADAS],
                    SECCION_REGISTRADAS,
                    politica,
                    importar_evidencias,
                    simulacion,
                    ruta_paquete,
                    conteos,
                    archivos_nuevos,
                    archivos_antiguos,
                )

            if simulacion:
                transaction.set_rollback(True)
            else:
                for nombre, novedad_pk in archivos_antiguos:
                    transaction.on_commit(
                        lambda nombre=nombre, novedad_pk=novedad_pk: (
                            _eliminar_evidencia_si_no_compartida(
                                nombre,
                                novedad_pk,
                            )
                        )
                    )
    except Exception:
        for nombre in archivos_nuevos:
            default_storage.delete(nombre)
        raise

    resultado = {
        "simulacion": simulacion,
        "secciones": list(secciones),
        "conteos": {seccion: dict(valores) for seccion, valores in conteos.items()},
        "respaldo_previo": str(respaldo) if respaldo else "",
        "sha256_paquete": inspeccion.sha256,
    }
    return resultado
