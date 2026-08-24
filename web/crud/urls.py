from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.bitaturno import views as bitaturno_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("transferencias/", include("apps.data_transfer.urls")),
    path(
        "media/<path:ruta>",
        bitaturno_views.archivo_media,
        name="archivo_media",
    ),
    path("", include("apps.bitaturno.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
