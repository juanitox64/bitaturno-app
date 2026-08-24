from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def puede_administrar_transferencias(usuario):
    return (
        usuario.is_authenticated
        and usuario.is_staff
        and (
            usuario.is_superuser
            or usuario.has_perm("data_transfer.can_manage_data_transfers")
        )
    )


def requiere_transferencias(vista):
    @login_required
    @wraps(vista)
    def protegida(request, *args, **kwargs):
        if not puede_administrar_transferencias(request.user):
            raise PermissionDenied(
                "No tiene permiso para administrar transferencias de datos."
            )
        return vista(request, *args, **kwargs)

    return protegida

