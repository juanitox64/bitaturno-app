import hashlib
import json
import shutil
import stat
import tempfile
import zipfile
from io import BytesIO, StringIO
from pathlib import Path
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.bitaturno.models import (
    Area,
    Disciplina,
    Equipo,
    Novedad,
    TipoNovedad,
    Turno,
)

from .models import Transferencia
from .services.constantes import (
    ARCHIVOS_SECCION,
    FORMATO_NOMBRE,
    FORMATO_VERSION,
    SECCION_BORRADORES,
    SECCION_CATALOGOS,
    SECCION_EVIDENCIAS,
    SECCION_REGISTRADAS,
    SECCION_USUARIOS,
)
from .services.excepciones import (
    ConflictoImportacion,
    ErrorTransferencia,
    PaqueteInvalido,
)
from .services.exportacion import crear_paquete_exportacion
from .services.importacion import ejecutar_importacion
from .services.paquetes import inspeccionar_paquete


TEST_ROOT = Path(tempfile.mkdtemp(prefix="bitaturno-transfer-tests-"))
TEST_MEDIA = TEST_ROOT / "media"
TEST_WORK = TEST_ROOT / "work"


def tearDownModule():
    shutil.rmtree(TEST_ROOT, ignore_errors=True)


def imagen(nombre="evidencia.jpg", formato="JPEG", color=(35, 90, 120)):
    contenido = BytesIO()
    Image.new("RGB", (20, 20), color).save(contenido, format=formato)
    return SimpleUploadedFile(
        nombre,
        contenido.getvalue(),
        content_type=f"image/{formato.lower()}",
    )


def sha(contenido):
    return hashlib.sha256(contenido).hexdigest()


@override_settings(
    MEDIA_ROOT=TEST_MEDIA,
    DATA_TRANSFER_WORK_ROOT=TEST_WORK,
    DATA_TRANSFER_UPLOAD_ROOT=TEST_WORK / "cargas",
    DATA_TRANSFER_EXPORT_ROOT=TEST_WORK / "exportaciones",
    DATA_TRANSFER_BACKUP_ROOT=TEST_WORK / "respaldos",
    SECURE_SSL_REDIRECT=False,
)
class TransferenciaDatosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        cls.admin = Usuario.objects.create_superuser(
            username="administrador",
            password="Clave-generica-123",
        )
        cls.operador = Usuario.objects.create_user(
            username="operador",
            password="Clave-generica-456",
            is_staff=True,
        )
        permiso = Permission.objects.get(
            codename="can_manage_data_transfers",
        )
        cls.operador.user_permissions.add(permiso)
        cls.usuario = Usuario.objects.create_user(
            username="usuario_generico",
            password="Clave-generica-789",
        )
        cls.disciplina = Disciplina.objects.create(nombre="Disciplina 1")
        cls.tipo = TipoNovedad.objects.create(nombre="Tipo 1")
        cls.turno = Turno.objects.create(nombre="Turno A")
        cls.area = Area.objects.create(nombre="Área 1")
        cls.equipo = Equipo.objects.create(codigo="EQ-001")

    def setUp(self):
        TEST_MEDIA.mkdir(parents=True, exist_ok=True)
        TEST_WORK.mkdir(parents=True, exist_ok=True)

    def crear_registrada(self, usuario=None, con_foto=True, titulo="Registro 1"):
        return Novedad.objects.create(
            titulo=titulo,
            descripcion_inicial="Descripción genérica.",
            disciplina=self.disciplina,
            tipo_novedad=self.tipo,
            turno=self.turno,
            area=self.area,
            equipo=self.equipo,
            prioridad=Novedad.Prioridad.MEDIA,
            estado_registro=Novedad.EstadoRegistro.REGISTRADA,
            estado_operacional=Novedad.EstadoOperacional.PENDIENTE,
            fecha_finalizacion=timezone.now(),
            fotografia=imagen() if con_foto else None,
            creado_por=usuario or self.usuario,
        )

    def crear_borrador(self, usuario=None):
        return Novedad.objects.create(
            descripcion_inicial="Borrador genérico.",
            estado_registro=Novedad.EstadoRegistro.BORRADOR,
            estado_operacional="",
            creado_por=usuario or self.usuario,
        )

    def ruta(self, nombre):
        ruta = TEST_ROOT / f"{uuid4().hex}-{nombre}"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        return ruta

    def exportar(
        self,
        secciones=None,
        evidencias=False,
        nombre="paquete.zip",
    ):
        ruta = self.ruta(nombre)
        return crear_paquete_exportacion(
            ruta,
            secciones=secciones
            or [
                SECCION_CATALOGOS,
                SECCION_USUARIOS,
                SECCION_BORRADORES,
                SECCION_REGISTRADAS,
            ],
            incluir_evidencias=evidencias,
        )

    def reescribir_zip(self, ruta, transformador):
        with zipfile.ZipFile(ruta, "r") as origen:
            archivos = {
                info.filename: origen.read(info.filename)
                for info in origen.infolist()
                if not info.is_dir()
            }
        archivos.pop("checksums.json", None)
        transformador(archivos)
        checksums = {
            nombre: sha(contenido)
            for nombre, contenido in sorted(archivos.items())
        }
        archivos["checksums.json"] = json.dumps(
            checksums,
            sort_keys=True,
        ).encode()
        with zipfile.ZipFile(
            ruta,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as destino:
            for nombre, contenido in archivos.items():
                destino.writestr(nombre, contenido)

    def eliminar_datos_portables(self):
        Novedad.objects.all().delete()
        for modelo in (Disciplina, TipoNovedad, Turno, Area, Equipo):
            modelo.objects.all().delete()
        get_user_model().objects.filter(username="usuario_generico").delete()

    def test_permisos_de_interfaz(self):
        url = reverse("data_transfer:inicio")
        respuesta = self.client.get(url)
        self.assertRedirects(respuesta, f"{reverse('bitaturno:login')}?next={url}")

        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_login(self.operador)
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Transferencia de datos")

    def test_exportacion_modular_no_incluye_credenciales(self):
        self.usuario.set_password("No-debe-aparecer-123")
        self.usuario.save()
        hash_contrasena = self.usuario.password.encode()
        inspeccion = self.exportar(
            secciones=[SECCION_USUARIOS],
            nombre="usuarios.zip",
        )
        self.assertEqual(inspeccion.secciones, (SECCION_USUARIOS,))
        with zipfile.ZipFile(inspeccion.ruta) as paquete:
            nombres = set(paquete.namelist())
            self.assertIn(ARCHIVOS_SECCION[SECCION_USUARIOS], nombres)
            self.assertNotIn(ARCHIVOS_SECCION[SECCION_CATALOGOS], nombres)
            usuarios = json.loads(
                paquete.read(ARCHIVOS_SECCION[SECCION_USUARIOS])
            )
            self.assertTrue(usuarios)
            self.assertEqual(set(usuarios[0]), {"username"})
            combinado = b"".join(
                paquete.read(nombre) for nombre in paquete.namelist()
            )
        self.assertNotIn(hash_contrasena, combinado)
        self.assertNotIn(b"is_superuser", combinado)
        self.assertNotIn(b"user_permissions", combinado)

    def test_exportacion_completa_con_evidencia_y_checksums(self):
        novedad = self.crear_registrada()
        self.crear_borrador()
        inspeccion = self.exportar(evidencias=True)
        self.assertEqual(
            inspeccion.manifest["formato"],
            FORMATO_NOMBRE,
        )
        self.assertEqual(inspeccion.manifest["version"], FORMATO_VERSION)
        self.assertEqual(inspeccion.conteos[SECCION_EVIDENCIAS], 1)
        with zipfile.ZipFile(inspeccion.ruta) as paquete:
            registradas = json.loads(
                paquete.read(ARCHIVOS_SECCION[SECCION_REGISTRADAS])
            )
            registro = next(
                item
                for item in registradas
                if item["portable_id"] == str(novedad.portable_id)
            )
            self.assertTrue(registro["fotografia"]["incluida"])
            self.assertIn(registro["fotografia"]["ruta"], paquete.namelist())
            checksums = json.loads(paquete.read("checksums.json"))
            for nombre, esperado in checksums.items():
                self.assertEqual(sha(paquete.read(nombre)), esperado)

    def test_rechaza_checksum_alterado(self):
        inspeccion = self.exportar(secciones=[SECCION_CATALOGOS])

        def alterar_readme(archivos):
            checksums_originales = json.loads(archivos["checksums.json"])
            archivos["README.txt"] = b"contenido alterado"
            archivos["checksums.json"] = json.dumps(
                checksums_originales
            ).encode()

        with zipfile.ZipFile(inspeccion.ruta, "r") as origen:
            archivos = {
                info.filename: origen.read(info.filename)
                for info in origen.infolist()
            }
        alterar_readme(archivos)
        with zipfile.ZipFile(inspeccion.ruta, "w") as destino:
            for nombre, contenido in archivos.items():
                destino.writestr(nombre, contenido)
        with self.assertRaises(PaqueteInvalido):
            inspeccionar_paquete(inspeccion.ruta)

    def test_rechaza_zip_slip_enlace_y_ejecutable(self):
        for nombre, info in (
            ("zip-slip.zip", zipfile.ZipInfo("../salida.txt")),
            ("absoluta.zip", zipfile.ZipInfo("/salida.txt")),
        ):
            ruta = self.ruta(nombre)
            with zipfile.ZipFile(ruta, "w") as paquete:
                paquete.writestr(info, b"x")
            with self.assertRaises(PaqueteInvalido):
                inspeccionar_paquete(ruta)

        ruta_enlace = self.ruta("enlace.zip")
        info_enlace = zipfile.ZipInfo("evidencias/enlace.jpg")
        info_enlace.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(ruta_enlace, "w") as paquete:
            paquete.writestr(info_enlace, b"destino")
        with self.assertRaises(PaqueteInvalido):
            inspeccionar_paquete(ruta_enlace)

        ruta_ejecutable = self.ruta("ejecutable.zip")
        info_ejecutable = zipfile.ZipInfo("README.txt")
        info_ejecutable.external_attr = (stat.S_IFREG | 0o755) << 16
        with zipfile.ZipFile(ruta_ejecutable, "w") as paquete:
            paquete.writestr(info_ejecutable, b"x")
        with self.assertRaises(PaqueteInvalido):
            inspeccionar_paquete(ruta_ejecutable)

    @override_settings(
        DATA_TRANSFER_MAX_FILES=2,
        DATA_TRANSFER_MAX_UNCOMPRESSED_BYTES=20,
    )
    def test_rechaza_exceso_de_archivos_y_expansion(self):
        ruta = self.ruta("muchos.zip")
        with zipfile.ZipFile(ruta, "w") as paquete:
            paquete.writestr("manifest.json", b"{}")
            paquete.writestr("checksums.json", b"{}")
            paquete.writestr("README.txt", b"x")
        with self.assertRaises(PaqueteInvalido):
            inspeccionar_paquete(ruta)

        ruta = self.ruta("expansion.zip")
        with zipfile.ZipFile(
            ruta,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as paquete:
            paquete.writestr("README.txt", b"x" * 21)
        with self.assertRaises(PaqueteInvalido):
            inspeccionar_paquete(ruta)

    def test_rechaza_imagen_falsa_aunque_tenga_checksum_valido(self):
        ruta = self.ruta("imagen-falsa.zip")
        ruta_evidencia = f"evidencias/{uuid4()}.jpg"
        manifest = {
            "formato": FORMATO_NOMBRE,
            "version": FORMATO_VERSION,
            "secciones": [SECCION_EVIDENCIAS],
            "conteos": {SECCION_EVIDENCIAS: 1},
        }
        archivos = {
            "manifest.json": json.dumps(manifest).encode(),
            "README.txt": b"paquete",
            ruta_evidencia: b"esto no es una imagen",
        }
        checksums = {
            nombre: sha(contenido) for nombre, contenido in archivos.items()
        }
        archivos["checksums.json"] = json.dumps(checksums).encode()
        with zipfile.ZipFile(ruta, "w") as paquete:
            for nombre, contenido in archivos.items():
                paquete.writestr(nombre, contenido)
        with self.assertRaises(PaqueteInvalido):
            inspeccionar_paquete(ruta)

    def test_simulacion_revierte_base_y_no_crea_archivos(self):
        self.crear_registrada()
        inspeccion = self.exportar(evidencias=True)
        self.eliminar_datos_portables()
        carpeta = TEST_MEDIA / "novedades" / "transferencias"
        if carpeta.exists():
            shutil.rmtree(carpeta)
        conteos_antes = {
            "disciplinas": Disciplina.objects.count(),
            "usuarios": get_user_model().objects.count(),
            "novedades": Novedad.objects.count(),
        }
        resultado = ejecutar_importacion(
            inspeccion.ruta,
            secciones=list(inspeccion.secciones),
            politica=Transferencia.Politica.OMITIR,
            simulacion=True,
        )
        self.assertTrue(resultado["simulacion"])
        self.assertEqual(Disciplina.objects.count(), conteos_antes["disciplinas"])
        self.assertEqual(get_user_model().objects.count(), conteos_antes["usuarios"])
        self.assertEqual(Novedad.objects.count(), conteos_antes["novedades"])
        self.assertFalse(carpeta.exists())

    def test_importacion_real_crea_usuario_inactivo_y_roundtrip(self):
        origen = self.crear_registrada()
        fecha_origen = origen.fecha_captura
        inspeccion = self.exportar(evidencias=True)
        portable_id = origen.portable_id
        self.eliminar_datos_portables()

        resultado = ejecutar_importacion(
            inspeccion.ruta,
            secciones=list(inspeccion.secciones),
            politica=Transferencia.Politica.OMITIR,
            simulacion=False,
        )
        importada = Novedad.objects.get(portable_id=portable_id)
        usuario = get_user_model().objects.get(username="usuario_generico")
        self.assertFalse(usuario.is_active)
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertFalse(usuario.has_usable_password())
        self.assertFalse(usuario.user_permissions.exists())
        self.assertEqual(importada.fecha_captura, fecha_origen)
        self.assertTrue(importada.fotografia)
        self.assertTrue(Path(importada.fotografia.path).is_file())
        self.assertTrue(Path(resultado["respaldo_previo"]).is_file())

    def test_actualizacion_preserva_password_y_privilegios(self):
        paquete = self.exportar(
            secciones=[SECCION_USUARIOS],
            nombre="preservar-usuarios.zip",
        )
        password = self.admin.password
        permisos = set(self.admin.user_permissions.values_list("pk", flat=True))
        resultado = ejecutar_importacion(
            paquete.ruta,
            secciones=[SECCION_USUARIOS],
            politica=Transferencia.Politica.ACTUALIZAR,
            simulacion=False,
        )
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.password, password)
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.is_superuser)
        self.assertEqual(
            set(self.admin.user_permissions.values_list("pk", flat=True)),
            permisos,
        )
        self.assertGreater(
            resultado["conteos"][SECCION_USUARIOS]["preservados"],
            0,
        )

    def test_politicas_omitir_actualizar_y_detener(self):
        paquete = self.exportar(secciones=[SECCION_CATALOGOS])
        self.disciplina.nombre = "Disciplina temporal"
        self.disciplina.save()

        ejecutar_importacion(
            paquete.ruta,
            secciones=[SECCION_CATALOGOS],
            politica=Transferencia.Politica.OMITIR,
            simulacion=False,
        )
        self.disciplina.refresh_from_db()
        self.assertEqual(self.disciplina.nombre, "Disciplina temporal")

        ejecutar_importacion(
            paquete.ruta,
            secciones=[SECCION_CATALOGOS],
            politica=Transferencia.Politica.ACTUALIZAR,
            simulacion=False,
        )
        self.disciplina.refresh_from_db()
        self.assertEqual(self.disciplina.nombre, "Disciplina 1")

        with self.assertRaises(ConflictoImportacion):
            ejecutar_importacion(
                paquete.ruta,
                secciones=[SECCION_CATALOGOS],
                politica=Transferencia.Politica.DETENER,
                simulacion=True,
            )

    def test_error_tardio_revierte_registros_y_evidencias(self):
        primera = self.crear_registrada(titulo="Registro 1")
        self.crear_registrada(titulo="Registro 2")
        paquete = self.exportar(evidencias=True)

        def cambiar_autor(archivos):
            nombre = ARCHIVOS_SECCION[SECCION_REGISTRADAS]
            datos = json.loads(archivos[nombre])
            datos[-1]["creado_por"] = "usuario_ausente"
            archivos[nombre] = json.dumps(
                datos,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ).encode()

        self.reescribir_zip(paquete.ruta, cambiar_autor)
        inspeccionar_paquete(paquete.ruta)
        self.eliminar_datos_portables()
        carpeta = TEST_MEDIA / "novedades" / "transferencias"
        if carpeta.exists():
            shutil.rmtree(carpeta)

        with self.assertRaises(ErrorTransferencia):
            ejecutar_importacion(
                paquete.ruta,
                secciones=[
                    SECCION_CATALOGOS,
                    SECCION_USUARIOS,
                    SECCION_REGISTRADAS,
                    SECCION_EVIDENCIAS,
                ],
                politica=Transferencia.Politica.OMITIR,
                simulacion=False,
            )
        self.assertFalse(Novedad.objects.filter(portable_id=primera.portable_id).exists())
        self.assertFalse(Disciplina.objects.exists())
        self.assertFalse(get_user_model().objects.filter(username="usuario_generico").exists())
        self.assertFalse(carpeta.exists() and any(carpeta.iterdir()))

    def test_flujo_web_inspeccion_simulacion_y_cancelacion(self):
        self.crear_registrada()
        paquete = self.exportar(evidencias=True)
        self.client.force_login(self.operador)
        with paquete.ruta.open("rb") as archivo:
            respuesta = self.client.post(
                reverse("data_transfer:cargar"),
                {
                    "paquete": SimpleUploadedFile(
                        "paquete.zip",
                        archivo.read(),
                        content_type="application/zip",
                    )
                },
            )
        self.assertEqual(respuesta.status_code, 302)
        token = respuesta.url.rstrip("/").split("/")[-1]
        pagina = self.client.get(respuesta.url)
        self.assertContains(pagina, "Paquete validado")

        total_antes = Novedad.objects.count()
        simulacion = self.client.post(
            respuesta.url,
            {
                "secciones": list(paquete.secciones),
                "politica": Transferencia.Politica.OMITIR,
                "accion": "simular",
            },
        )
        self.assertEqual(simulacion.status_code, 200)
        self.assertContains(simulacion, "Simulación completada")
        self.assertEqual(Novedad.objects.count(), total_antes)
        self.assertTrue(
            Transferencia.objects.filter(
                estado=Transferencia.Estado.SIMULADA
            ).exists()
        )

        cancelacion = self.client.post(
            reverse("data_transfer:inspeccionar", args=[token]),
            {"accion": "cancelar"},
            follow=True,
        )
        self.assertContains(cancelacion, "Importación cancelada")
        self.assertTrue(
            Transferencia.objects.filter(
                estado=Transferencia.Estado.CANCELADA
            ).exists()
        )

    def test_importacion_web_exige_confirmacion_literal(self):
        paquete = self.exportar(secciones=[SECCION_CATALOGOS])
        self.client.force_login(self.admin)
        with paquete.ruta.open("rb") as archivo:
            respuesta = self.client.post(
                reverse("data_transfer:cargar"),
                {
                    "paquete": SimpleUploadedFile(
                        "catalogos.zip",
                        archivo.read(),
                        content_type="application/zip",
                    )
                },
            )
        pagina = self.client.post(
            respuesta.url,
            {
                "secciones": [SECCION_CATALOGOS],
                "politica": Transferencia.Politica.OMITIR,
                "confirmacion": "importar",
                "accion": "importar",
            },
        )
        self.assertEqual(pagina.status_code, 400)
        self.assertContains(
            pagina,
            "Escriba exactamente",
            status_code=400,
        )

    def test_comandos_exportar_e_importar_dry_run(self):
        self.crear_borrador()
        salida = self.ruta("comando.zip")
        stdout = StringIO()
        call_command(
            "bitaturno_exportar",
            str(salida),
            "--secciones",
            SECCION_CATALOGOS,
            SECCION_BORRADORES,
            "--usuario",
            self.admin.username,
            stdout=stdout,
        )
        self.assertTrue(salida.is_file())
        self.assertIn("Paquete creado", stdout.getvalue())

        stdout = StringIO()
        call_command(
            "bitaturno_importar",
            str(salida),
            "--dry-run",
            "--usuario",
            self.admin.username,
            stdout=stdout,
        )
        self.assertIn("Simulación completada", stdout.getvalue())
        self.assertTrue(
            Transferencia.objects.filter(
                estado=Transferencia.Estado.SIMULADA
            ).exists()
        )

        with self.assertRaises(CommandError):
            call_command(
                "bitaturno_importar",
                str(salida),
                "--usuario",
                self.admin.username,
            )
