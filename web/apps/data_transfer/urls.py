from django.urls import path

from . import views

app_name = "data_transfer"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("exportar/", views.exportar, name="exportar"),
    path("cargar/", views.cargar, name="cargar"),
    path("inspeccionar/<uuid:token>/", views.inspeccionar, name="inspeccionar"),
    path("historial/<int:pk>/", views.detalle, name="detalle"),
    path(
        "historial/<int:pk>/descargar/",
        views.descargar,
        name="descargar",
    ),
]

