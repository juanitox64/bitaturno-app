from pathlib import Path

from django import forms
from django.conf import settings

from .models import Transferencia
from .services.constantes import (
    SECCION_BORRADORES,
    SECCION_CATALOGOS,
    SECCION_EVIDENCIAS,
    SECCION_REGISTRADAS,
    SECCION_USUARIOS,
)


ETIQUETAS_SECCIONES = {
    SECCION_CATALOGOS: "Catálogos",
    SECCION_USUARIOS: "Usuarios",
    SECCION_BORRADORES: "Borradores",
    SECCION_REGISTRADAS: "Novedades registradas",
    SECCION_EVIDENCIAS: "Evidencias fotográficas",
}


class ExportacionForm(forms.Form):
    secciones = forms.MultipleChoiceField(
        label="Secciones",
        choices=[
            (SECCION_CATALOGOS, ETIQUETAS_SECCIONES[SECCION_CATALOGOS]),
            (SECCION_USUARIOS, ETIQUETAS_SECCIONES[SECCION_USUARIOS]),
            (SECCION_BORRADORES, ETIQUETAS_SECCIONES[SECCION_BORRADORES]),
            (SECCION_REGISTRADAS, ETIQUETAS_SECCIONES[SECCION_REGISTRADAS]),
        ],
        widget=forms.CheckboxSelectMultiple,
    )
    incluir_evidencias = forms.BooleanField(
        label="Incluir evidencias fotográficas",
        required=False,
        help_text=(
            "Solo incorpora fotografías de los borradores o novedades "
            "seleccionados."
        ),
    )

    def clean(self):
        datos = super().clean()
        secciones = set(datos.get("secciones") or [])
        if datos.get("incluir_evidencias") and not {
            SECCION_BORRADORES,
            SECCION_REGISTRADAS,
        }.intersection(secciones):
            self.add_error(
                "incluir_evidencias",
                "Seleccione borradores o novedades registradas.",
            )
        return datos


class CargaPaqueteForm(forms.Form):
    paquete = forms.FileField(
        label="Paquete ZIP",
        help_text="Máximo 64 MB. Solo paquetes generados por BitaTurno.",
        widget=forms.ClearableFileInput(attrs={"accept": ".zip,application/zip"}),
    )

    def clean_paquete(self):
        paquete = self.cleaned_data["paquete"]
        nombre = paquete.name.replace("\\", "/").split("/")[-1]
        if Path(nombre).suffix.lower() != ".zip":
            raise forms.ValidationError("Seleccione un archivo con extensión .zip.")
        if paquete.size <= 0:
            raise forms.ValidationError("El paquete está vacío.")
        if paquete.size > settings.DATA_TRANSFER_MAX_PACKAGE_BYTES:
            raise forms.ValidationError("El paquete supera el máximo de 64 MB.")
        paquete.nombre_seguro = nombre
        return paquete


class OpcionesImportacionForm(forms.Form):
    secciones = forms.MultipleChoiceField(
        label="Secciones a importar",
        widget=forms.CheckboxSelectMultiple,
    )
    politica = forms.ChoiceField(
        label="Si el UUID ya existe",
        choices=Transferencia.Politica.choices,
        initial=Transferencia.Politica.OMITIR,
    )
    confirmacion = forms.CharField(
        label="Confirmación para importar",
        required=False,
        help_text=(
            'Para una importación real escriba exactamente "IMPORTAR". '
            "La simulación no requiere confirmación."
        ),
    )

    def __init__(self, *args, secciones_disponibles=(), **kwargs):
        super().__init__(*args, **kwargs)
        disponibles = list(secciones_disponibles)
        self.fields["secciones"].choices = [
            (seccion, ETIQUETAS_SECCIONES[seccion])
            for seccion in disponibles
        ]
        if not self.is_bound:
            self.initial["secciones"] = disponibles

    def clean(self):
        datos = super().clean()
        secciones = set(datos.get("secciones") or [])
        if SECCION_EVIDENCIAS in secciones and not {
            SECCION_BORRADORES,
            SECCION_REGISTRADAS,
        }.intersection(secciones):
            self.add_error(
                "secciones",
                "Las evidencias deben importarse junto con sus novedades.",
            )
        return datos

