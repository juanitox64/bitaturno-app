import mimetypes
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    EstadoOperacionalForm,
    FiltroHistoricoForm,
    LoginForm,
    NovedadForm,
)
from .models import Novedad


@login_required
def archivo_media(request, ruta):
    novedad = get_object_or_404(
        Novedad.objects.only(
            "fotografia",
            "estado_registro",
            "creado_por_id",
        ),
        fotografia=ruta,
    )
    if novedad.es_borrador and not (
        novedad.creado_por_id == request.user.id
        or request.user.is_staff
        or request.user.is_superuser
    ):
        raise Http404("El archivo solicitado no está disponible.")

    try:
        archivo = default_storage.open(ruta, "rb")
    except FileNotFoundError as error:
        raise Http404("El archivo solicitado no existe.") from error

    tipos_imagen = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    tipo_contenido = tipos_imagen.get(
        Path(ruta).suffix.lower(),
        mimetypes.guess_type(ruta)[0] or "application/octet-stream",
    )
    respuesta = FileResponse(archivo, content_type=tipo_contenido)
    respuesta["Content-Disposition"] = 'inline; filename="fotografia"'
    respuesta["X-Content-Type-Options"] = "nosniff"
    return respuesta


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("bitaturno:inicio")

    form = LoginForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        destino = request.POST.get("next", "")
        if not url_has_allowed_host_and_scheme(
            destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            destino = reverse("bitaturno:inicio")
        return redirect(destino)

    return render(
        request,
        "bitaturno/login.html",
        {"form": form, "next": request.GET.get("next", "")},
    )


@login_required
@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect("bitaturno:login")


@login_required
def inicio(request):
    resumen = Novedad.objects.aggregate(
        total_registradas=Count(
            "pk", filter=Q(estado_registro=Novedad.EstadoRegistro.REGISTRADA)
        ),
        pendientes=Count(
            "pk", filter=Q(estado_operacional=Novedad.EstadoOperacional.PENDIENTE)
        ),
        en_revision=Count(
            "pk", filter=Q(estado_operacional=Novedad.EstadoOperacional.EN_REVISION)
        ),
        cerradas=Count(
            "pk", filter=Q(estado_operacional=Novedad.EstadoOperacional.CERRADA)
        ),
    )
    resumen["mis_borradores"] = Novedad.objects.filter(
        estado_registro=Novedad.EstadoRegistro.BORRADOR,
        creado_por=request.user,
    ).count()
    return render(request, "bitaturno/inicio.html", {"resumen": resumen})


def _guardar_desde_formulario(form, usuario, accion):
    novedad = form.save(commit=False)
    if not novedad.pk:
        novedad.creado_por = usuario

    if accion == NovedadForm.ACCION_FINALIZAR:
        novedad.estado_registro = Novedad.EstadoRegistro.REGISTRADA
        novedad.estado_operacional = Novedad.EstadoOperacional.PENDIENTE
        novedad.fecha_finalizacion = timezone.now()
    else:
        novedad.estado_registro = Novedad.EstadoRegistro.BORRADOR
        novedad.estado_operacional = ""
        novedad.fecha_finalizacion = None
        novedad.fecha_cierre = None

    novedad.full_clean()
    novedad.save()
    return novedad


@login_required
def nueva_novedad(request):
    accion = request.POST.get("accion") if request.method == "POST" else None
    form = NovedadForm(
        request.POST or None,
        request.FILES or None,
        accion=accion,
    )
    if request.method == "POST" and form.is_valid():
        novedad = _guardar_desde_formulario(form, request.user, accion)
        if novedad.es_borrador:
            messages.success(request, "Borrador guardado. Aún no integra la bitácora oficial.")
            return redirect("bitaturno:editar_borrador", pk=novedad.pk)
        messages.success(request, "Novedad finalizada y registrada como pendiente.")
        return redirect("bitaturno:detalle", pk=novedad.pk)

    return render(
        request,
        "bitaturno/novedad_form.html",
        {"form": form, "es_edicion": False},
    )


@login_required
def mis_borradores(request):
    borradores = (
        Novedad.objects.filter(
            estado_registro=Novedad.EstadoRegistro.BORRADOR,
            creado_por=request.user,
        )
        .select_related("disciplina", "tipo_novedad", "turno")
        .order_by("-fecha_actualizacion")
    )
    return render(
        request, "bitaturno/mis_borradores.html", {"borradores": borradores}
    )


@login_required
def editar_borrador(request, pk):
    borrador = get_object_or_404(
        Novedad,
        pk=pk,
        estado_registro=Novedad.EstadoRegistro.BORRADOR,
        creado_por=request.user,
    )
    accion = request.POST.get("accion") if request.method == "POST" else None
    form = NovedadForm(
        request.POST or None,
        request.FILES or None,
        instance=borrador,
        accion=accion,
    )
    if request.method == "POST" and form.is_valid():
        novedad = _guardar_desde_formulario(form, request.user, accion)
        if novedad.es_borrador:
            messages.success(request, "Borrador actualizado.")
            return redirect("bitaturno:editar_borrador", pk=novedad.pk)
        messages.success(request, "Novedad finalizada y registrada como pendiente.")
        return redirect("bitaturno:detalle", pk=novedad.pk)

    return render(
        request,
        "bitaturno/novedad_form.html",
        {"form": form, "es_edicion": True, "novedad": borrador},
    )


@login_required
def historico(request):
    novedades = Novedad.objects.filter(
        estado_registro=Novedad.EstadoRegistro.REGISTRADA
    ).select_related("disciplina", "turno", "creado_por")
    filtros = FiltroHistoricoForm(request.GET or None)

    if filtros.is_valid():
        if filtros.cleaned_data["disciplina"]:
            novedades = novedades.filter(
                disciplina=filtros.cleaned_data["disciplina"]
            )
        if filtros.cleaned_data["turno"]:
            novedades = novedades.filter(turno=filtros.cleaned_data["turno"])
        if filtros.cleaned_data["prioridad"]:
            novedades = novedades.filter(
                prioridad=filtros.cleaned_data["prioridad"]
            )
        if filtros.cleaned_data["estado_operacional"]:
            novedades = novedades.filter(
                estado_operacional=filtros.cleaned_data["estado_operacional"]
            )

    return render(
        request,
        "bitaturno/historico.html",
        {"novedades": novedades, "filtros": filtros},
    )


@login_required
def detalle(request, pk):
    novedad = get_object_or_404(
        Novedad.objects.select_related(
            "disciplina",
            "tipo_novedad",
            "turno",
            "area",
            "equipo",
            "creado_por",
        ),
        pk=pk,
    )
    if novedad.es_borrador and not (
        novedad.creado_por_id == request.user.id
        or request.user.is_staff
        or request.user.is_superuser
    ):
        raise Http404("La novedad solicitada no está disponible.")
    return render(request, "bitaturno/detalle.html", {"novedad": novedad})


@login_required
def cambiar_estado(request, pk):
    novedad = get_object_or_404(
        Novedad,
        pk=pk,
        estado_registro=Novedad.EstadoRegistro.REGISTRADA,
    )
    form = EstadoOperacionalForm(
        request.POST or None,
        initial={"estado_operacional": novedad.estado_operacional},
    )
    if request.method == "POST" and form.is_valid():
        nuevo_estado = form.cleaned_data["estado_operacional"]
        novedad.estado_operacional = nuevo_estado
        novedad.save(
            update_fields=("estado_operacional", "fecha_actualizacion")
        )
        messages.success(request, "Estado operacional actualizado.")
        return redirect("bitaturno:detalle", pk=novedad.pk)

    return render(
        request,
        "bitaturno/cambiar_estado.html",
        {"form": form, "novedad": novedad},
    )


@login_required
def eliminar_borrador(request, pk):
    borrador = get_object_or_404(
        Novedad,
        pk=pk,
        estado_registro=Novedad.EstadoRegistro.BORRADOR,
        creado_por=request.user,
    )
    if request.method == "POST":
        borrador.delete()
        messages.success(request, "Borrador eliminado.")
        return redirect("bitaturno:mis_borradores")
    return render(
        request,
        "bitaturno/confirmar_eliminacion.html",
        {"novedad": borrador},
    )
