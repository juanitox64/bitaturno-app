from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...models import Transferencia
from ...services.constantes import SECCIONES_DATOS, SECCION_EVIDENCIAS
from ...services.excepciones import ErrorTransferencia
from ...services.exportacion import crear_paquete_exportacion


class Command(BaseCommand):
    help = "Exporta un paquete lógico y portable de BitaTurno."

    def add_arguments(self, parser):
        parser.add_argument("salida", type=Path)
        parser.add_argument(
            "--secciones",
            nargs="+",
            choices=SECCIONES_DATOS,
            default=list(SECCIONES_DATOS),
        )
        parser.add_argument(
            "--incluir-evidencias",
            action="store_true",
        )
        parser.add_argument(
            "--usuario",
            required=True,
            help="Usuario administrador que quedará en el historial.",
        )

    def handle(self, *args, **opciones):
        Usuario = get_user_model()
        try:
            usuario = Usuario.objects.get(username=opciones["usuario"])
        except Usuario.DoesNotExist as error:
            raise CommandError("El usuario de auditoría no existe.") from error
        if not usuario.is_staff:
            raise CommandError("El usuario de auditoría debe ser administrador.")

        secciones = opciones["secciones"]
        incluir = opciones["incluir_evidencias"]
        registro = Transferencia.objects.create(
            tipo=Transferencia.Tipo.EXPORTACION,
            estado=Transferencia.Estado.INSPECCIONADA,
            usuario=usuario,
            secciones=secciones + ([SECCION_EVIDENCIAS] if incluir else []),
            opciones={"incluir_evidencias": incluir, "origen": "comando"},
            nombre_paquete=opciones["salida"].name,
        )
        try:
            inspeccion = crear_paquete_exportacion(
                opciones["salida"],
                secciones=secciones,
                incluir_evidencias=incluir,
            )
        except ErrorTransferencia as error:
            registro.estado = Transferencia.Estado.FALLIDA
            registro.fecha_fin = timezone.now()
            registro.errores = str(error)
            registro.save(update_fields=("estado", "fecha_fin", "errores"))
            raise CommandError(str(error)) from error

        registro.estado = Transferencia.Estado.COMPLETADA
        registro.fecha_fin = timezone.now()
        registro.sha256_paquete = inspeccion.sha256
        registro.tamano_paquete = inspeccion.tamano
        registro.archivo_ruta = str(opciones["salida"].resolve())
        registro.conteos = inspeccion.conteos
        registro.resultado = {"mensaje": "Exportación completada por comando."}
        registro.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Paquete creado: {opciones['salida']} "
                f"(SHA-256 {inspeccion.sha256})"
            )
        )

