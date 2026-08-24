from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...models import Transferencia
from ...services.constantes import SECCIONES_TODAS
from ...services.excepciones import ErrorTransferencia
from ...services.importacion import ejecutar_importacion
from ...services.paquetes import inspeccionar_paquete


class Command(BaseCommand):
    help = "Simula o ejecuta una importación lógica de BitaTurno."

    def add_arguments(self, parser):
        parser.add_argument("paquete", type=Path)
        parser.add_argument(
            "--secciones",
            nargs="+",
            choices=SECCIONES_TODAS,
        )
        parser.add_argument(
            "--politica",
            choices=Transferencia.Politica.values,
            default=Transferencia.Politica.OMITIR,
        )
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--confirmar",
            default="",
            help='Para importar realmente debe indicar --confirmar IMPORTAR.',
        )
        parser.add_argument(
            "--usuario",
            required=True,
            help="Usuario administrador que quedará en el historial.",
        )

    def handle(self, *args, **opciones):
        if not opciones["dry_run"] and opciones["confirmar"] != "IMPORTAR":
            raise CommandError(
                'La importación real requiere "--confirmar IMPORTAR".'
            )

        Usuario = get_user_model()
        try:
            usuario = Usuario.objects.get(username=opciones["usuario"])
        except Usuario.DoesNotExist as error:
            raise CommandError("El usuario de auditoría no existe.") from error
        if not usuario.is_staff:
            raise CommandError("El usuario de auditoría debe ser administrador.")

        try:
            inspeccion = inspeccionar_paquete(opciones["paquete"])
        except ErrorTransferencia as error:
            raise CommandError(str(error)) from error
        secciones = opciones["secciones"] or list(inspeccion.secciones)
        simulacion = opciones["dry_run"]
        registro = Transferencia.objects.create(
            tipo=Transferencia.Tipo.IMPORTACION,
            estado=Transferencia.Estado.INSPECCIONADA,
            usuario=usuario,
            secciones=secciones,
            opciones={"simulacion": simulacion, "origen": "comando"},
            politica=opciones["politica"],
            nombre_paquete=opciones["paquete"].name,
            sha256_paquete=inspeccion.sha256,
            tamano_paquete=inspeccion.tamano,
            conteos=inspeccion.conteos,
        )
        try:
            resultado = ejecutar_importacion(
                opciones["paquete"],
                secciones=secciones,
                politica=opciones["politica"],
                simulacion=simulacion,
            )
        except ErrorTransferencia as error:
            registro.estado = Transferencia.Estado.FALLIDA
            registro.fecha_fin = timezone.now()
            registro.errores = str(error)
            registro.save(update_fields=("estado", "fecha_fin", "errores"))
            raise CommandError(str(error)) from error

        registro.estado = (
            Transferencia.Estado.SIMULADA
            if simulacion
            else Transferencia.Estado.COMPLETADA
        )
        registro.fecha_fin = timezone.now()
        registro.respaldo_previo = resultado["respaldo_previo"]
        registro.resultado = resultado
        registro.save()
        mensaje = (
            "Simulación completada; no se modificaron datos."
            if simulacion
            else "Importación completada."
        )
        self.stdout.write(self.style.SUCCESS(mensaje))

