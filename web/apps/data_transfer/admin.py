from django.contrib import admin

from .models import Transferencia


@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = (
        "tipo",
        "estado",
        "nombre_paquete",
        "usuario",
        "fecha_inicio",
        "fecha_fin",
    )
    list_filter = ("tipo", "estado", "politica")
    search_fields = ("nombre_paquete", "usuario__username", "sha256_paquete")
    readonly_fields = (
        "portable_id",
        "tipo",
        "estado",
        "usuario",
        "fecha_inicio",
        "fecha_fin",
        "secciones",
        "opciones",
        "politica",
        "nombre_paquete",
        "sha256_paquete",
        "tamano_paquete",
        "archivo_ruta",
        "respaldo_previo",
        "conteos",
        "resultado",
        "errores",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

