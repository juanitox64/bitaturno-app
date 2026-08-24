from django.contrib import admin

from .models import Area, Disciplina, Equipo, Novedad, TipoNovedad, Turno


class CatalogoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo", "fecha_actualizacion")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Disciplina)
class DisciplinaAdmin(CatalogoAdmin):
    pass


@admin.register(TipoNovedad)
class TipoNovedadAdmin(CatalogoAdmin):
    pass


@admin.register(Turno)
class TurnoAdmin(CatalogoAdmin):
    pass


@admin.register(Area)
class AreaAdmin(CatalogoAdmin):
    pass


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "activo", "fecha_actualizacion")
    list_filter = ("activo",)
    search_fields = ("codigo",)
    ordering = ("codigo",)


@admin.register(Novedad)
class NovedadAdmin(admin.ModelAdmin):
    list_display = (
        "titulo_o_borrador",
        "estado_registro",
        "estado_operacional",
        "prioridad",
        "turno",
        "creado_por",
        "fecha_captura",
    )
    list_filter = (
        "estado_registro",
        "estado_operacional",
        "prioridad",
        "disciplina",
        "turno",
    )
    search_fields = (
        "titulo",
        "descripcion_inicial",
        "equipo__codigo",
        "creado_por__username",
    )
    autocomplete_fields = ("creado_por",)
    readonly_fields = (
        "fecha_captura",
        "fecha_actualizacion",
        "fecha_finalizacion",
        "fecha_cierre",
    )
    date_hierarchy = "fecha_captura"

    @admin.display(description="Novedad")
    def titulo_o_borrador(self, obj):
        return str(obj)


admin.site.site_header = "Administración de BitaTurno"
admin.site.site_title = "BitaTurno Admin"
admin.site.index_title = "Catálogos, usuarios y novedades"

