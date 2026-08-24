import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from .imagenes import (
    MAXIMO_FOTOGRAFIA_ORIGINAL_BYTES,
    optimizar_fotografia,
)


MAXIMO_FOTOGRAFIA_BYTES = MAXIMO_FOTOGRAFIA_ORIGINAL_BYTES


def validar_tamano_fotografia(archivo):
    if archivo.size > MAXIMO_FOTOGRAFIA_BYTES:
        raise ValidationError("La fotografía original no puede superar 25 MB.")


class CatalogoBase(models.Model):
    portable_id = models.UUIDField(
        "identificador portable",
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    nombre = models.CharField("nombre", max_length=100, unique=True)
    activo = models.BooleanField("activo", default=True)
    fecha_creacion = models.DateTimeField("fecha de creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("fecha de actualización", auto_now=True)

    class Meta:
        abstract = True
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre


class Disciplina(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "disciplina"
        verbose_name_plural = "disciplinas"


class TipoNovedad(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "tipo de novedad"
        verbose_name_plural = "tipos de novedad"


class Turno(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "turno"
        verbose_name_plural = "turnos"


class Area(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "área"
        verbose_name_plural = "áreas"


class Equipo(models.Model):
    portable_id = models.UUIDField(
        "identificador portable",
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    codigo = models.CharField("código", max_length=50, unique=True)
    activo = models.BooleanField("activo", default=True)
    fecha_creacion = models.DateTimeField("fecha de creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("fecha de actualización", auto_now=True)

    class Meta:
        ordering = ("codigo",)
        verbose_name = "equipo"
        verbose_name_plural = "equipos"

    def clean(self):
        super().clean()
        self.codigo = (self.codigo or "").strip().upper()
        if not self.codigo:
            raise ValidationError({"codigo": "El código es obligatorio."})

    def save(self, *args, **kwargs):
        self.codigo = (self.codigo or "").strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo


class Novedad(models.Model):
    class Prioridad(models.TextChoices):
        BAJA = "BAJA", "Baja"
        MEDIA = "MEDIA", "Media"
        ALTA = "ALTA", "Alta"

    class EstadoRegistro(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        REGISTRADA = "REGISTRADA", "Registrada"

    class EstadoOperacional(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_REVISION = "EN_REVISION", "En revisión"
        CERRADA = "CERRADA", "Cerrada"

    portable_id = models.UUIDField(
        "identificador portable",
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    titulo = models.CharField("título", max_length=180, blank=True)
    descripcion_inicial = models.TextField("descripción inicial", blank=True)
    disciplina = models.ForeignKey(
        Disciplina,
        verbose_name="disciplina",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="novedades",
    )
    tipo_novedad = models.ForeignKey(
        TipoNovedad,
        verbose_name="tipo de novedad",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="novedades",
    )
    turno = models.ForeignKey(
        Turno,
        verbose_name="turno",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="novedades",
    )
    area = models.ForeignKey(
        Area,
        verbose_name="área",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="novedades",
    )
    equipo = models.ForeignKey(
        Equipo,
        verbose_name="equipo",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="novedades",
    )
    prioridad = models.CharField(
        "prioridad",
        max_length=5,
        choices=Prioridad.choices,
        blank=True,
        default="",
    )
    estado_registro = models.CharField(
        "estado del registro",
        max_length=10,
        choices=EstadoRegistro.choices,
        default=EstadoRegistro.BORRADOR,
        editable=False,
    )
    estado_operacional = models.CharField(
        "estado operacional",
        max_length=11,
        choices=EstadoOperacional.choices,
        blank=True,
        default="",
    )
    fecha_ocurrencia = models.DateTimeField(
        "fecha y hora de ocurrencia",
        null=True,
        blank=True,
        help_text="Opcional. Corresponde al momento informado por el usuario.",
    )
    fecha_captura = models.DateTimeField("fecha de captura", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("fecha de actualización", auto_now=True)
    fecha_finalizacion = models.DateTimeField(
        "fecha de finalización", null=True, blank=True, editable=False
    )
    fecha_cierre = models.DateTimeField(
        "fecha de cierre", null=True, blank=True, editable=False
    )
    fotografia = models.ImageField(
        "fotografía",
        upload_to="novedades/%Y/%m/",
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=("jpg", "jpeg", "png", "webp"),
                message="Formato no permitido. Use JPEG, PNG o WEBP.",
            ),
            validar_tamano_fotografia,
        ],
        help_text=(
            "Opcional. JPEG, PNG o WEBP; original de hasta 25 MB. "
            "Se optimiza automáticamente a un máximo de 3 MB."
        ),
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="creado por",
        on_delete=models.PROTECT,
        related_name="novedades_creadas",
    )

    class Meta:
        ordering = ("-fecha_captura", "-pk")
        verbose_name = "novedad"
        verbose_name_plural = "novedades"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(estado_registro="BORRADOR", estado_operacional="")
                    | Q(
                        estado_registro="REGISTRADA",
                        estado_operacional__in=(
                            "PENDIENTE",
                            "EN_REVISION",
                            "CERRADA",
                        ),
                    )
                ),
                name="bitaturno_estado_registro_operacional_valido",
            )
        ]

    def _sincronizar_fecha_cierre(self):
        estado_anterior = None
        fecha_cierre_anterior = None
        if self.pk:
            anterior = (
                type(self)
                .objects.filter(pk=self.pk)
                .values("estado_operacional", "fecha_cierre")
                .first()
            )
            if anterior:
                estado_anterior = anterior["estado_operacional"]
                fecha_cierre_anterior = anterior["fecha_cierre"]

        esta_cerrada = (
            self.estado_registro == self.EstadoRegistro.REGISTRADA
            and self.estado_operacional == self.EstadoOperacional.CERRADA
        )
        if not esta_cerrada:
            self.fecha_cierre = None
        elif (
            estado_anterior == self.EstadoOperacional.CERRADA
            and fecha_cierre_anterior
        ):
            self.fecha_cierre = fecha_cierre_anterior
        elif not self.fecha_cierre:
            self.fecha_cierre = timezone.now()

    def _optimizar_fotografia_nueva(self):
        if not self.fotografia or self.fotografia._committed:
            return

        archivo = self.fotografia.file
        type(self)._meta.get_field("fotografia").run_validators(archivo)
        if getattr(archivo, "_bitaturno_optimizada", False):
            return
        self.fotografia = optimizar_fotografia(archivo)

    def save(self, *args, **kwargs):
        self._optimizar_fotografia_nueva()
        fecha_cierre_recibida = self.fecha_cierre
        self._sincronizar_fecha_cierre()

        update_fields = kwargs.get("update_fields")
        if update_fields is not None and self.fecha_cierre != fecha_cierre_recibida:
            kwargs["update_fields"] = tuple(
                set(update_fields) | {"fecha_cierre"}
            )

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        self.titulo = (self.titulo or "").strip()
        self.descripcion_inicial = (self.descripcion_inicial or "").strip()

        errores = {}
        if self.estado_registro == self.EstadoRegistro.BORRADOR:
            if self.estado_operacional:
                errores["estado_operacional"] = (
                    "Un borrador no puede tener estado operacional."
                )
            if not self.descripcion_inicial and not self.fotografia:
                mensaje = "Un borrador requiere una descripción o fotografía."
                errores["descripcion_inicial"] = mensaje
                errores["fotografia"] = mensaje
        elif self.estado_registro == self.EstadoRegistro.REGISTRADA:
            requeridos = {
                "titulo": self.titulo,
                "descripcion_inicial": self.descripcion_inicial,
                "disciplina": self.disciplina_id,
                "tipo_novedad": self.tipo_novedad_id,
                "turno": self.turno_id,
                "prioridad": self.prioridad,
            }
            for campo, valor in requeridos.items():
                if not valor:
                    errores[campo] = "Este campo es obligatorio al finalizar."
            if self.estado_operacional not in self.EstadoOperacional.values:
                errores["estado_operacional"] = (
                    "Una novedad registrada debe tener estado operacional."
                )
            if not self.fecha_finalizacion:
                errores["fecha_finalizacion"] = (
                    "Una novedad registrada debe tener fecha de finalización."
                )

        if errores:
            raise ValidationError(errores)

    def campos_faltantes_finalizacion(self):
        campos = (
            ("Título", self.titulo),
            ("Descripción inicial", self.descripcion_inicial),
            ("Disciplina", self.disciplina_id),
            ("Tipo de novedad", self.tipo_novedad_id),
            ("Turno", self.turno_id),
            ("Prioridad", self.prioridad),
        )
        return [etiqueta for etiqueta, valor in campos if not valor]

    @property
    def es_borrador(self):
        return self.estado_registro == self.EstadoRegistro.BORRADOR

    def get_absolute_url(self):
        return reverse("bitaturno:detalle", kwargs={"pk": self.pk})

    def __str__(self):
        return self.titulo or f"Borrador #{self.pk or 'nuevo'}"
