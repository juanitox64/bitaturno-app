from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q

from .imagenes import optimizar_fotografia
from .models import Area, Disciplina, Equipo, Novedad, TipoNovedad, Turno


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", max_length=150)
    password = forms.CharField(label="Contraseña", strip=False, widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "Usuario o contraseña incorrectos.",
        "inactive": "Esta cuenta está inactiva.",
    }


class NovedadForm(forms.ModelForm):
    ACCION_BORRADOR = "guardar_borrador"
    ACCION_FINALIZAR = "finalizar"
    ACCIONES = {ACCION_BORRADOR, ACCION_FINALIZAR}

    class Meta:
        model = Novedad
        fields = (
            "titulo",
            "descripcion_inicial",
            "disciplina",
            "tipo_novedad",
            "turno",
            "area",
            "equipo",
            "prioridad",
            "fecha_ocurrencia",
            "fotografia",
        )
        widgets = {
            "descripcion_inicial": forms.Textarea(
                attrs={"rows": 6, "placeholder": "Describa la novedad observada"}
            ),
            "fecha_ocurrencia": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "fotografia": forms.ClearableFileInput(
                attrs={
                    "accept": "image/jpeg,image/png,image/webp",
                    "data-max-original-bytes": str(25 * 1024 * 1024),
                    "data-max-final-bytes": str(3 * 1024 * 1024),
                    "data-max-dimension": "2048",
                }
            ),
        }

    def __init__(self, *args, accion=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.accion = accion
        self.fields["fecha_ocurrencia"].input_formats = ("%Y-%m-%dT%H:%M",)
        self._configurar_catalogos()

    def _configurar_catalogos(self):
        catalogos = {
            "disciplina": Disciplina,
            "tipo_novedad": TipoNovedad,
            "turno": Turno,
            "area": Area,
            "equipo": Equipo,
        }
        for nombre_campo, modelo in catalogos.items():
            actual_id = getattr(self.instance, f"{nombre_campo}_id", None)
            filtro = Q(activo=True)
            if actual_id:
                filtro |= Q(pk=actual_id)
            self.fields[nombre_campo].queryset = modelo.objects.filter(filtro)
            self.fields[nombre_campo].empty_label = "Seleccione una opción"

    def clean_fotografia(self):
        fotografia = self.cleaned_data.get("fotografia")
        if isinstance(fotografia, UploadedFile):
            Novedad._meta.get_field("fotografia").run_validators(fotografia)
            return optimizar_fotografia(fotografia)
        return fotografia

    def clean(self):
        datos = super().clean()
        if self.accion not in self.ACCIONES:
            raise forms.ValidationError("Seleccione una acción válida para el registro.")

        titulo = (datos.get("titulo") or "").strip()
        descripcion = (datos.get("descripcion_inicial") or "").strip()
        datos["titulo"] = titulo
        datos["descripcion_inicial"] = descripcion

        fotografia = datos.get("fotografia")
        if fotografia is False:
            tiene_fotografia = False
        elif fotografia:
            tiene_fotografia = True
        else:
            tiene_fotografia = bool(self.instance.pk and self.instance.fotografia)

        if not descripcion and not tiene_fotografia:
            self.add_error(
                "descripcion_inicial",
                "Para guardar un borrador debe ingresar una descripción o fotografía.",
            )
            self.add_error(
                "fotografia",
                "Para guardar un borrador debe ingresar una descripción o fotografía.",
            )

        if self.accion == self.ACCION_FINALIZAR:
            requeridos = {
                "titulo": titulo,
                "descripcion_inicial": descripcion,
                "disciplina": datos.get("disciplina"),
                "tipo_novedad": datos.get("tipo_novedad"),
                "turno": datos.get("turno"),
                "prioridad": datos.get("prioridad"),
            }
            for campo, valor in requeridos.items():
                if not valor:
                    self.add_error(
                        campo, "Este campo es obligatorio para finalizar el registro."
                    )

        return datos


class FiltroHistoricoForm(forms.Form):
    disciplina = forms.ModelChoiceField(
        label="Disciplina", queryset=Disciplina.objects.none(), required=False
    )
    turno = forms.ModelChoiceField(
        label="Turno", queryset=Turno.objects.none(), required=False
    )
    prioridad = forms.ChoiceField(
        label="Prioridad",
        choices=[("", "Todas"), *Novedad.Prioridad.choices],
        required=False,
    )
    estado_operacional = forms.ChoiceField(
        label="Estado",
        choices=[("", "Todos"), *Novedad.EstadoOperacional.choices],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["disciplina"].queryset = Disciplina.objects.all()
        self.fields["disciplina"].empty_label = "Todas"
        self.fields["turno"].queryset = Turno.objects.all()
        self.fields["turno"].empty_label = "Todos"


class EstadoOperacionalForm(forms.Form):
    estado_operacional = forms.ChoiceField(
        label="Nuevo estado", choices=Novedad.EstadoOperacional.choices
    )
