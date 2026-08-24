from django.urls import path

from . import views

app_name = "bitaturno"

urlpatterns = [
    path("", views.iniciar_sesion, name="login"),
    path("salir/", views.cerrar_sesion, name="logout"),
    path("inicio/", views.inicio, name="inicio"),
    path("novedades/nueva/", views.nueva_novedad, name="nueva"),
    path("novedades/historico/", views.historico, name="historico"),
    path("novedades/<int:pk>/", views.detalle, name="detalle"),
    path(
        "novedades/<int:pk>/estado/",
        views.cambiar_estado,
        name="cambiar_estado",
    ),
    path("borradores/", views.mis_borradores, name="mis_borradores"),
    path(
        "borradores/<int:pk>/editar/",
        views.editar_borrador,
        name="editar_borrador",
    ),
    path(
        "borradores/<int:pk>/eliminar/",
        views.eliminar_borrador,
        name="eliminar_borrador",
    ),
]

