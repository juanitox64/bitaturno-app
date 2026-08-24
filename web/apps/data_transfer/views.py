from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CargaPaqueteForm, ExportacionForm, OpcionesImportacionForm
from .models import Transferencia
from .permisos import requiere_transferencias
from .services import (
    crear_paquete_exportacion,
    ejecutar_importacion,
    inspeccionar_paquete,
)
from .services.constantes import SECCION_EVIDENCIAS
from .services.excepciones import ErrorTransferencia


CLAVE_SESION = "data_transfer_paquetes"


def _terminar(registro, estado, resultado=None, errores=""):
    registro.estado = estado
    registro.fecha_fin = timezone.now()
    registro.resultado = resultado or {}
    registro.errores = errores
    registro.save(
        update_fields=("estado", "fecha_fin", "resultado", "errores")
    )


def _ruta_en_raiz(ruta, raiz):
    try:
        return Path(ruta).resolve().is_relative_to(Path(raiz).resolve())
    except (OSError, ValueError):
        return False


def _paquete_sesion(request, token):
    paquetes = request.session.get(CLAVE_SESION, {})
    datos = paquetes.get(str(token))
    if not datos:
        raise Http404("El paquete temporal no está disponible.")
    ruta = Path(datos["ruta"])
    if (
        not _ruta_en_raiz(ruta, settings.DATA_TRANSFER_UPLOAD_ROOT)
        or not ruta.is_file()
    ):
        raise Http404("El paquete temporal no está disponible.")
    return ruta, datos["nombre"]


def _quitar_paquete_sesion(request, token, eliminar=True):
    paquetes = request.session.get(CLAVE_SESION, {})
    datos = paquetes.pop(str(token), None)
    request.session[CLAVE_SESION] = paquetes
    request.session.modified = True
    if datos and eliminar:
        ruta = Path(datos["ruta"])
        if _ruta_en_raiz(ruta, settings.DATA_TRANSFER_UPLOAD_ROOT):
            ruta.unlink(missing_ok=True)


@requiere_transferencias
def inicio(request):
    historial = Transferencia.objects.select_related("usuario")[:30]
    return render(
        request,
        "data_transfer/inicio.html",
        {
            "exportacion_form": ExportacionForm(),
            "carga_form": CargaPaqueteForm(),
            "historial": historial,
        },
    )


@requiere_transferencias
@require_POST
def exportar(request):
    form = ExportacionForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "data_transfer/inicio.html",
            {
                "exportacion_form": form,
                "carga_form": CargaPaqueteForm(),
                "historial": Transferencia.objects.select_related("usuario")[:30],
            },
            status=400,
        )

    secciones = form.cleaned_data["secciones"]
    incluir_evidencias = form.cleaned_data["incluir_evidencias"]
    directorio = Path(settings.DATA_TRANSFER_EXPORT_ROOT)
    directorio.mkdir(parents=True, exist_ok=True)
    nombre = (
        f"bitaturno-{timezone.now().strftime('%Y%m%dT%H%M%SZ')}-"
        f"{uuid4().hex[:8]}.zip"
    )
    ruta = directorio / nombre
    registro = Transferencia.objects.create(
        tipo=Transferencia.Tipo.EXPORTACION,
        estado=Transferencia.Estado.INSPECCIONADA,
        usuario=request.user,
        secciones=secciones + (
            [SECCION_EVIDENCIAS] if incluir_evidencias else []
        ),
        opciones={"incluir_evidencias": incluir_evidencias},
        nombre_paquete=nombre,
    )
    try:
        inspeccion = crear_paquete_exportacion(
            ruta,
            secciones,
            incluir_evidencias=incluir_evidencias,
            limpiar_retencion=True,
        )
        registro.sha256_paquete = inspeccion.sha256
        registro.tamano_paquete = inspeccion.tamano
        registro.archivo_ruta = str(ruta)
        registro.conteos = inspeccion.conteos
        registro.save(
            update_fields=(
                "sha256_paquete",
                "tamano_paquete",
                "archivo_ruta",
                "conteos",
            )
        )
        _terminar(
            registro,
            Transferencia.Estado.COMPLETADA,
            {"mensaje": "Paquete exportado y validado."},
        )
    except ErrorTransferencia as error:
        _terminar(
            registro,
            Transferencia.Estado.FALLIDA,
            errores=str(error),
        )
        messages.error(request, str(error))
        return redirect("data_transfer:inicio")

    respuesta = FileResponse(
        ruta.open("rb"),
        as_attachment=True,
        filename=nombre,
        content_type="application/zip",
    )
    respuesta["X-Content-Type-Options"] = "nosniff"
    return respuesta


@requiere_transferencias
@require_POST
def cargar(request):
    form = CargaPaqueteForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(
            request,
            "data_transfer/inicio.html",
            {
                "exportacion_form": ExportacionForm(),
                "carga_form": form,
                "historial": Transferencia.objects.select_related("usuario")[:30],
            },
            status=400,
        )

    paquete = form.cleaned_data["paquete"]
    token = uuid4()
    directorio = Path(settings.DATA_TRANSFER_UPLOAD_ROOT)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / f"{token}.zip"
    total = 0
    try:
        with ruta.open("xb") as destino:
            for bloque in paquete.chunks():
                total += len(bloque)
                if total > settings.DATA_TRANSFER_MAX_PACKAGE_BYTES:
                    raise ErrorTransferencia(
                        "El paquete supera el tamaño permitido."
                    )
                destino.write(bloque)
        inspeccion = inspeccionar_paquete(ruta)
    except Exception as error:
        ruta.unlink(missing_ok=True)
        mensaje = (
            str(error)
            if isinstance(error, ErrorTransferencia)
            else "No fue posible almacenar el paquete."
        )
        form.add_error("paquete", mensaje)
        return render(
            request,
            "data_transfer/inicio.html",
            {
                "exportacion_form": ExportacionForm(),
                "carga_form": form,
                "historial": Transferencia.objects.select_related("usuario")[:30],
            },
            status=400,
        )

    paquetes = request.session.get(CLAVE_SESION, {})
    paquetes[str(token)] = {
        "ruta": str(ruta),
        "nombre": paquete.nombre_seguro,
    }
    request.session[CLAVE_SESION] = paquetes
    Transferencia.objects.create(
        tipo=Transferencia.Tipo.IMPORTACION,
        estado=Transferencia.Estado.INSPECCIONADA,
        usuario=request.user,
        fecha_fin=timezone.now(),
        secciones=list(inspeccion.secciones),
        nombre_paquete=paquete.nombre_seguro,
        sha256_paquete=inspeccion.sha256,
        tamano_paquete=inspeccion.tamano,
        conteos=inspeccion.conteos,
        resultado={"mensaje": "Paquete inspeccionado; no se modificaron datos."},
    )
    return redirect("data_transfer:inspeccionar", token=token)


@requiere_transferencias
def inspeccionar(request, token):
    ruta, nombre = _paquete_sesion(request, token)
    try:
        inspeccion_paquete = inspeccionar_paquete(ruta)
    except ErrorTransferencia as error:
        _quitar_paquete_sesion(request, token)
        messages.error(request, str(error))
        return redirect("data_transfer:inicio")

    if request.method == "POST" and request.POST.get("accion") == "cancelar":
        Transferencia.objects.create(
            tipo=Transferencia.Tipo.IMPORTACION,
            estado=Transferencia.Estado.CANCELADA,
            usuario=request.user,
            fecha_fin=timezone.now(),
            secciones=list(inspeccion_paquete.secciones),
            nombre_paquete=nombre,
            sha256_paquete=inspeccion_paquete.sha256,
            tamano_paquete=inspeccion_paquete.tamano,
            conteos=inspeccion_paquete.conteos,
            resultado={"mensaje": "Operación cancelada sin modificar datos."},
        )
        _quitar_paquete_sesion(request, token)
        messages.success(request, "Importación cancelada. No se modificaron datos.")
        return redirect("data_transfer:inicio")

    form = OpcionesImportacionForm(
        request.POST or None,
        secciones_disponibles=inspeccion_paquete.secciones,
    )
    if request.method == "POST" and form.is_valid():
        accion = request.POST.get("accion")
        simulacion = accion == "simular"
        if accion not in {"simular", "importar"}:
            form.add_error(None, "La acción solicitada no es válida.")
        elif not simulacion and form.cleaned_data["confirmacion"] != "IMPORTAR":
            form.add_error(
                "confirmacion",
                'Escriba exactamente "IMPORTAR" para confirmar.',
            )
        else:
            registro = Transferencia.objects.create(
                tipo=Transferencia.Tipo.IMPORTACION,
                estado=Transferencia.Estado.INSPECCIONADA,
                usuario=request.user,
                secciones=form.cleaned_data["secciones"],
                opciones={"simulacion": simulacion},
                politica=form.cleaned_data["politica"],
                nombre_paquete=nombre,
                sha256_paquete=inspeccion_paquete.sha256,
                tamano_paquete=inspeccion_paquete.tamano,
                conteos=inspeccion_paquete.conteos,
            )
            try:
                resultado = ejecutar_importacion(
                    ruta,
                    secciones=form.cleaned_data["secciones"],
                    politica=form.cleaned_data["politica"],
                    simulacion=simulacion,
                )
                registro.respaldo_previo = resultado["respaldo_previo"]
                registro.save(update_fields=("respaldo_previo",))
                _terminar(
                    registro,
                    (
                        Transferencia.Estado.SIMULADA
                        if simulacion
                        else Transferencia.Estado.COMPLETADA
                    ),
                    resultado,
                )
                if not simulacion:
                    _quitar_paquete_sesion(request, token)
                return render(
                    request,
                    "data_transfer/resultado.html",
                    {
                        "transferencia": registro,
                        "token": token if simulacion else None,
                    },
                )
            except ErrorTransferencia as error:
                _terminar(
                    registro,
                    Transferencia.Estado.FALLIDA,
                    errores=str(error),
                )
                form.add_error(None, str(error))

    return render(
        request,
        "data_transfer/inspeccionar.html",
        {
            "inspeccion": inspeccion_paquete,
            "nombre": nombre,
            "form": form,
            "token": token,
        },
        status=400 if request.method == "POST" and form.errors else 200,
    )


@requiere_transferencias
def detalle(request, pk):
    transferencia = get_object_or_404(
        Transferencia.objects.select_related("usuario"),
        pk=pk,
    )
    return render(
        request,
        "data_transfer/detalle.html",
        {"transferencia": transferencia},
    )


@requiere_transferencias
def descargar(request, pk):
    transferencia = get_object_or_404(
        Transferencia,
        pk=pk,
        tipo=Transferencia.Tipo.EXPORTACION,
        estado=Transferencia.Estado.COMPLETADA,
    )
    ruta = Path(transferencia.archivo_ruta)
    if (
        not _ruta_en_raiz(ruta, settings.DATA_TRANSFER_EXPORT_ROOT)
        or not ruta.is_file()
    ):
        raise Http404("El paquete exportado ya no está disponible.")
    respuesta = FileResponse(
        ruta.open("rb"),
        as_attachment=True,
        filename=transferencia.nombre_paquete,
        content_type="application/zip",
    )
    respuesta["X-Content-Type-Options"] = "nosniff"
    return respuesta

