import uuid

from django.conf import settings
from django.db import models


class Transferencia(models.Model):
    class Tipo(models.TextChoices):
        EXPORTACION = "EXPORTACION", "Exportación"
        IMPORTACION = "IMPORTACION", "Importación"

    class Estado(models.TextChoices):
        INSPECCIONADA = "INSPECCIONADA", "Inspeccionada"
        COMPLETADA = "COMPLETADA", "Completada"
        SIMULADA = "SIMULADA", "Simulada"
        CANCELADA = "CANCELADA", "Cancelada"
        FALLIDA = "FALLIDA", "Fallida"

    class Politica(models.TextChoices):
        OMITIR = "OMITIR", "Omitir existentes"
        ACTUALIZAR = "ACTUALIZAR", "Actualizar existentes"
        DETENER = "DETENER", "Detener ante conflictos"

    portable_id = models.UUIDField(
        "identificador",
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    tipo = models.CharField("tipo", max_length=12, choices=Tipo.choices)
    estado = models.CharField("estado", max_length=14, choices=Estado.choices)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuario",
        on_delete=models.PROTECT,
        related_name="transferencias_datos",
    )
    fecha_inicio = models.DateTimeField("fecha de inicio", auto_now_add=True)
    fecha_fin = models.DateTimeField("fecha de término", null=True, blank=True)
    secciones = models.JSONField("secciones", default=list)
    opciones = models.JSONField("opciones", default=dict)
    politica = models.CharField(
        "política de conflictos",
        max_length=10,
        choices=Politica.choices,
        blank=True,
    )
    nombre_paquete = models.CharField("nombre del paquete", max_length=255)
    sha256_paquete = models.CharField("SHA-256", max_length=64, blank=True)
    tamano_paquete = models.PositiveBigIntegerField("tamaño", default=0)
    archivo_ruta = models.CharField("ruta interna", max_length=500, blank=True)
    respaldo_previo = models.CharField(
        "respaldo previo",
        max_length=500,
        blank=True,
    )
    conteos = models.JSONField("conteos", default=dict)
    resultado = models.JSONField("resultado", default=dict)
    errores = models.TextField("errores", blank=True)

    class Meta:
        ordering = ("-fecha_inicio", "-pk")
        verbose_name = "transferencia de datos"
        verbose_name_plural = "transferencias de datos"
        permissions = [
            (
                "can_manage_data_transfers",
                "Puede administrar transferencias de datos",
            )
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.nombre_paquete}"

