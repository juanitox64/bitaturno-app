import shutil
import tempfile
from datetime import timedelta
from io import BytesIO
from pathlib import Path

from PIL import Image
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .imagenes import (
    MAXIMO_DIMENSION_FOTOGRAFIA,
    MAXIMO_FOTOGRAFIA_ALMACENADA_BYTES,
)
from .models import (
    MAXIMO_FOTOGRAFIA_BYTES,
    Area,
    Disciplina,
    Equipo,
    Novedad,
    TipoNovedad,
    Turno,
    validar_tamano_fotografia,
)


TEST_MEDIA_ROOT = Path(tempfile.gettempdir()) / "bitaturno_test_media"
User = get_user_model()


def fotografia_valida(nombre="foto.png"):
    contenido = BytesIO()
    Image.new("RGB", (2, 2), color=(40, 90, 120)).save(contenido, format="PNG")
    return SimpleUploadedFile(
        nombre,
        contenido.getvalue(),
        content_type="image/png",
    )


def fotografia_valida_con_tamano(tamano, nombre="foto.png"):
    contenido = BytesIO()
    Image.new("RGB", (2, 2), color=(40, 90, 120)).save(contenido, format="PNG")
    base = contenido.getvalue()
    if tamano < len(base):
        raise ValueError("El tamaño solicitado es menor que la imagen base.")
    return SimpleUploadedFile(
        nombre,
        base + (b"\0" * (tamano - len(base))),
        content_type="image/png",
    )


def fotografia_alta_resolucion(nombre="foto-alta-resolucion.jpg"):
    contenido = BytesIO()
    imagen = Image.effect_noise((3200, 2400), 100).convert("RGB")
    metadatos = Image.Exif()
    metadatos[270] = "Dato genérico que debe eliminarse"
    metadatos[274] = 6
    imagen.save(contenido, format="JPEG", quality=95, exif=metadatos)
    return SimpleUploadedFile(
        nombre,
        contenido.getvalue(),
        content_type="image/jpeg",
    )


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT, SECURE_SSL_REDIRECT=False)
class BitaTurnoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario1 = User.objects.create_user(
            username="usuario1", password="clave-prueba-1"
        )
        cls.usuario2 = User.objects.create_user(
            username="usuario2", password="clave-prueba-2"
        )
        cls.administrador = User.objects.create_superuser(
            username="administrador",
            email="admin@example.invalid",
            password="clave-prueba-admin",
        )
        cls.disciplina1 = Disciplina.objects.create(nombre="Disciplina 1")
        cls.disciplina2 = Disciplina.objects.create(nombre="Disciplina 2")
        cls.disciplina_inactiva = Disciplina.objects.create(
            nombre="Disciplina inactiva", activo=False
        )
        cls.tipo1 = TipoNovedad.objects.create(nombre="Tipo 1")
        cls.tipo2 = TipoNovedad.objects.create(nombre="Tipo 2")
        cls.turno_a = Turno.objects.create(nombre="Turno A")
        cls.turno_b = Turno.objects.create(nombre="Turno B")
        cls.area1 = Area.objects.create(nombre="Área 1")
        cls.equipo1 = Equipo.objects.create(codigo="EQ-001")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        ruta = TEST_MEDIA_ROOT.resolve()
        raiz = Path(tempfile.gettempdir()).resolve()
        if ruta.is_relative_to(raiz) and ruta.exists():
            shutil.rmtree(ruta)

    def datos_finalizacion(self, **cambios):
        datos = {
            "titulo": "Novedad 1",
            "descripcion_inicial": "Descripción inicial",
            "disciplina": self.disciplina1.pk,
            "tipo_novedad": self.tipo1.pk,
            "turno": self.turno_a.pk,
            "area": self.area1.pk,
            "equipo": self.equipo1.pk,
            "prioridad": Novedad.Prioridad.MEDIA,
            "fecha_ocurrencia": "",
            "accion": "finalizar",
        }
        datos.update(cambios)
        return datos

    def crear_borrador(self, usuario=None, **cambios):
        datos = {
            "descripcion_inicial": "Descripción de borrador",
            "estado_registro": Novedad.EstadoRegistro.BORRADOR,
            "estado_operacional": "",
            "creado_por": usuario or self.usuario1,
        }
        datos.update(cambios)
        return Novedad.objects.create(**datos)

    def crear_registrada(self, usuario=None, **cambios):
        datos = {
            "titulo": "Novedad 1",
            "descripcion_inicial": "Descripción inicial",
            "disciplina": self.disciplina1,
            "tipo_novedad": self.tipo1,
            "turno": self.turno_a,
            "prioridad": Novedad.Prioridad.MEDIA,
            "estado_registro": Novedad.EstadoRegistro.REGISTRADA,
            "estado_operacional": Novedad.EstadoOperacional.PENDIENTE,
            "fecha_finalizacion": timezone.now(),
            "creado_por": usuario or self.usuario1,
        }
        datos.update(cambios)
        return Novedad.objects.create(**datos)

    def test_pantallas_operacionales_redirigen_a_login_sin_sesion(self):
        rutas = (
            reverse("bitaturno:inicio"),
            reverse("bitaturno:nueva"),
            reverse("bitaturno:mis_borradores"),
            reverse("bitaturno:historico"),
        )
        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertRedirects(
                    respuesta, f"{reverse('bitaturno:login')}?next={ruta}"
                )

    def test_login_valido_e_invalido(self):
        respuesta_invalida = self.client.post(
            reverse("bitaturno:login"),
            {"username": "usuario1", "password": "incorrecta"},
        )
        self.assertEqual(respuesta_invalida.status_code, 200)
        self.assertContains(respuesta_invalida, "Usuario o contraseña incorrectos")

        respuesta_valida = self.client.post(
            reverse("bitaturno:login"),
            {"username": "usuario1", "password": "clave-prueba-1"},
        )
        self.assertRedirects(respuesta_valida, reverse("bitaturno:inicio"))

    def test_logout_solo_acepta_post(self):
        self.client.force_login(self.usuario1)
        self.assertEqual(self.client.get(reverse("bitaturno:logout")).status_code, 405)
        self.assertRedirects(
            self.client.post(reverse("bitaturno:logout")),
            reverse("bitaturno:login"),
        )

    def test_guardar_borrador_con_descripcion(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.post(
            reverse("bitaturno:nueva"),
            {
                "descripcion_inicial": "Descripción de borrador",
                "accion": "guardar_borrador",
            },
        )
        borrador = Novedad.objects.get()
        self.assertRedirects(
            respuesta, reverse("bitaturno:editar_borrador", args=(borrador.pk,))
        )
        self.assertEqual(borrador.creado_por, self.usuario1)
        self.assertEqual(borrador.estado_registro, Novedad.EstadoRegistro.BORRADOR)
        self.assertEqual(borrador.estado_operacional, "")

    def test_guardar_borrador_con_fotografia_sin_descripcion(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.post(
            reverse("bitaturno:nueva"),
            {
                "descripcion_inicial": "",
                "fotografia": fotografia_valida(),
                "accion": "guardar_borrador",
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        borrador = Novedad.objects.get()
        self.assertTrue(borrador.fotografia.name.endswith(".webp"))
        self.assertLessEqual(
            borrador.fotografia.size,
            MAXIMO_FOTOGRAFIA_ALMACENADA_BYTES,
        )
        self.assertEqual(borrador.descripcion_inicial, "")

    def test_rechazar_borrador_vacio(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.post(
            reverse("bitaturno:nueva"), {"accion": "guardar_borrador"}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            "Para guardar un borrador debe ingresar una descripción o fotografía",
        )
        self.assertEqual(Novedad.objects.count(), 0)

    def test_modelo_rechaza_borrador_vacio(self):
        borrador = Novedad(creado_por=self.usuario1)
        with self.assertRaises(ValidationError):
            borrador.full_clean()

    def test_editar_y_eliminar_borrador_propio_con_confirmacion(self):
        borrador = self.crear_borrador()
        self.client.force_login(self.usuario1)
        respuesta_edicion = self.client.post(
            reverse("bitaturno:editar_borrador", args=(borrador.pk,)),
            {
                "descripcion_inicial": "Descripción actualizada",
                "accion": "guardar_borrador",
            },
        )
        self.assertRedirects(
            respuesta_edicion,
            reverse("bitaturno:editar_borrador", args=(borrador.pk,)),
        )
        borrador.refresh_from_db()
        self.assertEqual(borrador.descripcion_inicial, "Descripción actualizada")

        url_eliminar = reverse("bitaturno:eliminar_borrador", args=(borrador.pk,))
        respuesta_confirmacion = self.client.get(url_eliminar)
        self.assertEqual(respuesta_confirmacion.status_code, 200)
        self.assertContains(respuesta_confirmacion, "Confirmar eliminación")
        self.assertTrue(Novedad.objects.filter(pk=borrador.pk).exists())

        self.assertRedirects(
            self.client.post(url_eliminar), reverse("bitaturno:mis_borradores")
        )
        self.assertFalse(Novedad.objects.filter(pk=borrador.pk).exists())

    def test_no_se_puede_editar_ver_ni_eliminar_borrador_ajeno(self):
        borrador = self.crear_borrador(usuario=self.usuario2)
        self.client.force_login(self.usuario1)
        rutas = (
            reverse("bitaturno:editar_borrador", args=(borrador.pk,)),
            reverse("bitaturno:detalle", args=(borrador.pk,)),
            reverse("bitaturno:eliminar_borrador", args=(borrador.pk,)),
        )
        for ruta in rutas:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(ruta).status_code, 404)
        self.assertTrue(Novedad.objects.filter(pk=borrador.pk).exists())

    def test_administrador_puede_ver_borrador_ajeno(self):
        borrador = self.crear_borrador(usuario=self.usuario2)
        self.client.force_login(self.administrador)
        respuesta = self.client.get(
            reverse("bitaturno:detalle", args=(borrador.pk,))
        )
        self.assertEqual(respuesta.status_code, 200)

    def test_rechazar_finalizacion_incompleta_con_campos_claros(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.post(
            reverse("bitaturno:nueva"),
            {
                "descripcion_inicial": "Descripción inicial",
                "accion": "finalizar",
            },
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta, "Este campo es obligatorio para finalizar el registro"
        )
        self.assertEqual(Novedad.objects.count(), 0)

    def test_finalizacion_valida_crea_registrada_pendiente(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.post(
            reverse("bitaturno:nueva"), self.datos_finalizacion()
        )
        novedad = Novedad.objects.get()
        self.assertRedirects(
            respuesta, reverse("bitaturno:detalle", args=(novedad.pk,))
        )
        self.assertEqual(
            novedad.estado_registro, Novedad.EstadoRegistro.REGISTRADA
        )
        self.assertEqual(
            novedad.estado_operacional, Novedad.EstadoOperacional.PENDIENTE
        )
        self.assertIsNotNone(novedad.fecha_finalizacion)

    def test_borradores_no_aparecen_en_historico_y_registradas_si(self):
        borrador = self.crear_borrador(titulo="Borrador 1")
        registrada = self.crear_registrada(titulo="Novedad registrada")
        self.client.force_login(self.usuario1)
        respuesta = self.client.get(reverse("bitaturno:historico"))
        self.assertNotContains(respuesta, borrador.titulo)
        self.assertContains(respuesta, registrada.titulo)

    def test_catalogos_activos_visibles_e_inactivos_ocultos_en_formulario_nuevo(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.get(reverse("bitaturno:nueva"))
        self.assertContains(respuesta, self.disciplina1.nombre)
        self.assertNotContains(respuesta, self.disciplina_inactiva.nombre)

    def test_formulario_muestra_aviso_limite_fotografia(self):
        borrador = self.crear_borrador()
        self.client.force_login(self.usuario1)
        rutas = (
            reverse("bitaturno:nueva"),
            reverse("bitaturno:editar_borrador", args=(borrador.pk,)),
        )

        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertContains(respuesta, "Fotografía opcional")
                self.assertContains(
                    respuesta,
                    "puede seleccionar un archivo JPEG, PNG o WEBP de hasta 25 MB",
                )
                self.assertContains(respuesta, "máximo de 3 MB y 2048 píxeles")
                self.assertContains(respuesta, "optimizar-fotografia.js")
                self.assertContains(
                    respuesta,
                    'data-max-original-bytes="26214400"',
                )

    def test_catalogo_inactivo_ya_usado_se_conserva_al_editar_borrador(self):
        borrador = self.crear_borrador(disciplina=self.disciplina_inactiva)
        self.client.force_login(self.usuario1)
        respuesta = self.client.get(
            reverse("bitaturno:editar_borrador", args=(borrador.pk,))
        )
        self.assertContains(respuesta, self.disciplina_inactiva.nombre)

    def test_codigo_equipo_se_normaliza_y_duplicado_se_rechaza(self):
        equipo = Equipo(codigo="  eq-002  ")
        equipo.full_clean()
        equipo.save()
        self.assertEqual(equipo.codigo, "EQ-002")

        duplicado = Equipo(codigo="eq-002")
        with self.assertRaises(ValidationError):
            duplicado.full_clean()

    def test_fotografia_valida_visible_en_detalle(self):
        novedad = self.crear_registrada(fotografia=fotografia_valida())
        self.client.force_login(self.usuario1)
        respuesta = self.client.get(
            reverse("bitaturno:detalle", args=(novedad.pk,))
        )
        self.assertContains(respuesta, novedad.fotografia.url)
        self.assertContains(respuesta, "Fotografía")

    def test_fotografia_registrada_requiere_sesion(self):
        novedad = self.crear_registrada(fotografia=fotografia_valida())
        ruta = novedad.fotografia.url

        respuesta_sin_sesion = self.client.get(ruta)
        self.assertEqual(respuesta_sin_sesion.status_code, 302)
        self.assertIn("next=", respuesta_sin_sesion.url)

        self.client.force_login(self.usuario2)
        respuesta_autenticada = self.client.get(ruta)
        self.assertEqual(respuesta_autenticada.status_code, 200)
        self.assertEqual(respuesta_autenticada["Content-Type"], "image/webp")
        novedad.refresh_from_db()
        self.assertTrue(novedad.fotografia.name.endswith(".webp"))
        self.assertLessEqual(
            novedad.fotografia.size,
            MAXIMO_FOTOGRAFIA_ALMACENADA_BYTES,
        )

    def test_fotografia_de_borrador_solo_es_visible_para_autor_y_admin(self):
        borrador = self.crear_borrador(fotografia=fotografia_valida())
        ruta = borrador.fotografia.url

        self.client.force_login(self.usuario2)
        self.assertEqual(self.client.get(ruta).status_code, 404)

        self.client.force_login(self.usuario1)
        self.assertEqual(self.client.get(ruta).status_code, 200)

        self.client.force_login(self.administrador)
        self.assertEqual(self.client.get(ruta).status_code, 200)

    def test_archivo_con_extension_invalida_es_rechazado(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.post(
            reverse("bitaturno:nueva"),
            {
                "descripcion_inicial": "Descripción inicial",
                "fotografia": fotografia_valida("foto.gif"),
                "accion": "guardar_borrador",
            },
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Formato no permitido")
        self.assertEqual(Novedad.objects.count(), 0)

    def test_fotografia_mayor_a_veinticinco_mb_es_rechazada_por_validador(self):
        archivo = SimpleUploadedFile(
            "grande.png",
            b"x" * (MAXIMO_FOTOGRAFIA_BYTES + 1),
            content_type="image/png",
        )
        with self.assertRaisesMessage(
            ValidationError, "La fotografía original no puede superar 25 MB"
        ):
            validar_tamano_fotografia(archivo)

    def test_imagen_mayor_25mb_rechazada_con_mensaje(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.post(
            reverse("bitaturno:nueva"),
            {
                "descripcion_inicial": "Descripción genérica",
                "fotografia": fotografia_valida_con_tamano(
                    MAXIMO_FOTOGRAFIA_BYTES + 1,
                    "supera-limite.png",
                ),
                "accion": "guardar_borrador",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            "La fotografía original no puede superar 25 MB",
        )
        self.assertEqual(Novedad.objects.count(), 0)

    def test_imagen_hasta_25mb_aceptada_y_optimizada(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.post(
            reverse("bitaturno:nueva"),
            {
                "descripcion_inicial": "Descripción genérica",
                "fotografia": fotografia_valida_con_tamano(
                    MAXIMO_FOTOGRAFIA_BYTES,
                    "limite.png",
                ),
                "accion": "guardar_borrador",
            },
        )

        self.assertEqual(respuesta.status_code, 302)
        borrador = Novedad.objects.get()
        self.assertTrue(borrador.fotografia.name.endswith(".webp"))
        self.assertLessEqual(
            borrador.fotografia.size,
            MAXIMO_FOTOGRAFIA_ALMACENADA_BYTES,
        )

    def test_imagen_alta_resolucion_se_reduce_y_elimina_metadatos(self):
        original = fotografia_alta_resolucion()
        self.assertGreater(original.size, MAXIMO_FOTOGRAFIA_ALMACENADA_BYTES)
        self.assertLessEqual(original.size, MAXIMO_FOTOGRAFIA_BYTES)
        self.client.force_login(self.usuario1)

        respuesta = self.client.post(
            reverse("bitaturno:nueva"),
            {
                "descripcion_inicial": "Descripción genérica",
                "fotografia": original,
                "accion": "guardar_borrador",
            },
        )

        self.assertEqual(respuesta.status_code, 302)
        borrador = Novedad.objects.get()
        self.assertLessEqual(
            borrador.fotografia.size,
            MAXIMO_FOTOGRAFIA_ALMACENADA_BYTES,
        )
        with borrador.fotografia.open("rb") as archivo:
            with Image.open(archivo) as optimizada:
                self.assertEqual(optimizada.format, "WEBP")
                self.assertLessEqual(
                    max(optimizada.size),
                    MAXIMO_DIMENSION_FOTOGRAFIA,
                )
                self.assertFalse(optimizada.getexif())

    def test_imagen_sobredimensionada_no_crea_registro_ni_archivo(self):
        archivos_antes = {
            archivo.relative_to(TEST_MEDIA_ROOT)
            for archivo in TEST_MEDIA_ROOT.rglob("*")
            if archivo.is_file()
        } if TEST_MEDIA_ROOT.exists() else set()
        self.client.force_login(self.usuario1)

        respuesta = self.client.post(
            reverse("bitaturno:nueva"),
            {
                "descripcion_inicial": "Descripción genérica",
                "fotografia": fotografia_valida_con_tamano(
                    MAXIMO_FOTOGRAFIA_BYTES + 1,
                    "no-guardar.png",
                ),
                "accion": "guardar_borrador",
            },
        )

        archivos_despues = {
            archivo.relative_to(TEST_MEDIA_ROOT)
            for archivo in TEST_MEDIA_ROOT.rglob("*")
            if archivo.is_file()
        } if TEST_MEDIA_ROOT.exists() else set()
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Novedad.objects.count(), 0)
        self.assertEqual(archivos_despues, archivos_antes)

    def test_finalizar_novedad_sin_fotografia(self):
        self.client.force_login(self.usuario1)
        respuesta = self.client.post(
            reverse("bitaturno:nueva"),
            self.datos_finalizacion(),
        )

        self.assertEqual(respuesta.status_code, 302)
        novedad = Novedad.objects.get()
        self.assertEqual(
            novedad.estado_registro,
            Novedad.EstadoRegistro.REGISTRADA,
        )
        self.assertFalse(novedad.fotografia)

    def test_filtros_por_disciplina_turno_prioridad_y_estado(self):
        incluida = self.crear_registrada(titulo="Novedad incluida")
        excluida = self.crear_registrada(
            titulo="Novedad excluida",
            disciplina=self.disciplina2,
            tipo_novedad=self.tipo2,
            turno=self.turno_b,
            prioridad=Novedad.Prioridad.ALTA,
            estado_operacional=Novedad.EstadoOperacional.CERRADA,
            fecha_cierre=timezone.now(),
        )
        self.client.force_login(self.usuario1)
        casos = (
            {"disciplina": incluida.disciplina_id},
            {"turno": incluida.turno_id},
            {"prioridad": incluida.prioridad},
            {"estado_operacional": incluida.estado_operacional},
        )
        for parametros in casos:
            with self.subTest(parametros=parametros):
                respuesta = self.client.get(
                    reverse("bitaturno:historico"), parametros
                )
                self.assertContains(respuesta, incluida.titulo)
                self.assertNotContains(respuesta, excluida.titulo)

    def test_cambio_de_estado_asigna_y_limpia_fecha_cierre(self):
        novedad = self.crear_registrada()
        self.client.force_login(self.usuario1)
        url = reverse("bitaturno:cambiar_estado", args=(novedad.pk,))

        self.assertRedirects(
            self.client.post(
                url,
                {"estado_operacional": Novedad.EstadoOperacional.CERRADA},
            ),
            reverse("bitaturno:detalle", args=(novedad.pk,)),
        )
        novedad.refresh_from_db()
        self.assertEqual(
            novedad.estado_operacional, Novedad.EstadoOperacional.CERRADA
        )
        self.assertIsNotNone(novedad.fecha_cierre)

        self.client.post(
            url,
            {"estado_operacional": Novedad.EstadoOperacional.EN_REVISION},
        )
        novedad.refresh_from_db()
        self.assertEqual(
            novedad.estado_operacional, Novedad.EstadoOperacional.EN_REVISION
        )
        self.assertIsNone(novedad.fecha_cierre)

    def test_cerrar_novedad_asigna_fecha_cierre(self):
        novedad = self.crear_registrada()
        novedad.estado_operacional = Novedad.EstadoOperacional.CERRADA
        novedad.save(update_fields=("estado_operacional", "fecha_actualizacion"))
        novedad.refresh_from_db()

        self.assertIsNotNone(novedad.fecha_cierre)

    def test_novedad_cerrada_conserva_fecha_si_no_hay_transicion(self):
        fecha_original = timezone.now() - timedelta(days=1)
        novedad = self.crear_registrada(
            estado_operacional=Novedad.EstadoOperacional.CERRADA,
            fecha_cierre=fecha_original,
        )

        novedad.titulo = "Título actualizado sin transición"
        novedad.save()
        novedad.refresh_from_db()

        self.assertEqual(novedad.fecha_cierre, fecha_original)

    def test_reabrir_novedad_limpia_fecha_cierre(self):
        novedad = self.crear_registrada(
            estado_operacional=Novedad.EstadoOperacional.CERRADA,
            fecha_cierre=timezone.now() - timedelta(days=1),
        )
        self.client.force_login(self.usuario1)

        respuesta = self.client.post(
            reverse("bitaturno:cambiar_estado", args=(novedad.pk,)),
            {"estado_operacional": Novedad.EstadoOperacional.EN_REVISION},
        )
        novedad.refresh_from_db()

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(
            novedad.estado_operacional,
            Novedad.EstadoOperacional.EN_REVISION,
        )
        self.assertIsNone(novedad.fecha_cierre)

    def test_cerrar_nuevamente_asigna_nueva_fecha(self):
        fecha_original = timezone.now() - timedelta(days=1)
        novedad = self.crear_registrada(
            estado_operacional=Novedad.EstadoOperacional.CERRADA,
            fecha_cierre=fecha_original,
        )
        self.client.force_login(self.usuario1)
        url = reverse("bitaturno:cambiar_estado", args=(novedad.pk,))

        self.client.post(
            url,
            {"estado_operacional": Novedad.EstadoOperacional.EN_REVISION},
        )
        self.client.post(
            url,
            {"estado_operacional": Novedad.EstadoOperacional.CERRADA},
        )
        novedad.refresh_from_db()

        self.assertIsNotNone(novedad.fecha_cierre)
        self.assertGreater(novedad.fecha_cierre, fecha_original)

    def test_contadores_reflejan_cierre_y_reapertura(self):
        novedad = self.crear_registrada()
        self.client.force_login(self.usuario1)
        url = reverse("bitaturno:cambiar_estado", args=(novedad.pk,))

        self.client.post(
            url,
            {"estado_operacional": Novedad.EstadoOperacional.CERRADA},
        )
        resumen_cierre = self.client.get(reverse("bitaturno:inicio")).context[
            "resumen"
        ]
        self.assertEqual(resumen_cierre["total_registradas"], 1)
        self.assertEqual(resumen_cierre["pendientes"], 0)
        self.assertEqual(resumen_cierre["cerradas"], 1)

        self.client.post(
            url,
            {"estado_operacional": Novedad.EstadoOperacional.EN_REVISION},
        )
        resumen_reapertura = self.client.get(reverse("bitaturno:inicio")).context[
            "resumen"
        ]
        self.assertEqual(resumen_reapertura["total_registradas"], 1)
        self.assertEqual(resumen_reapertura["cerradas"], 0)
        self.assertEqual(resumen_reapertura["en_revision"], 1)

    def test_editar_borrador_conserva_id_y_estado(self):
        borrador = self.crear_borrador()
        identificador = borrador.pk
        self.client.force_login(self.usuario1)
        url = reverse("bitaturno:editar_borrador", args=(identificador,))

        for intento in range(1, 6):
            datos = {
                "descripcion_inicial": f"Edición genérica {intento}",
                "accion": "guardar_borrador",
            }
            if intento % 2 == 0:
                datos["fotografia"] = fotografia_valida(f"edicion-{intento}.png")
            respuesta = self.client.post(url, datos, follow=True)

            with self.subTest(intento=intento):
                self.assertEqual(respuesta.redirect_chain, [(url, 302)])
                self.assertContains(respuesta, "Borrador actualizado")
                borrador.refresh_from_db()
                self.assertEqual(borrador.pk, identificador)
                self.assertEqual(
                    borrador.estado_registro,
                    Novedad.EstadoRegistro.BORRADOR,
                )
                self.assertEqual(Novedad.objects.count(), 1)

    def test_editar_borrador_no_duplica_registro(self):
        borrador = self.crear_borrador()
        self.client.force_login(self.usuario1)
        url = reverse("bitaturno:editar_borrador", args=(borrador.pk,))

        for intento in range(1, 6):
            self.client.post(
                url,
                {
                    "descripcion_inicial": f"Actualización {intento}",
                    "accion": "guardar_borrador",
                },
            )

        self.assertEqual(Novedad.objects.count(), 1)
        self.assertTrue(Novedad.objects.filter(pk=borrador.pk).exists())

    def test_usuario_normal_no_edita_novedad_finalizada_por_url(self):
        novedad = self.crear_registrada(usuario=self.usuario1)
        descripcion_original = novedad.descripcion_inicial
        self.client.force_login(self.usuario1)
        url = reverse("bitaturno:editar_borrador", args=(novedad.pk,))

        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(
            self.client.post(
                url,
                {
                    "descripcion_inicial": "Intento de cambio",
                    "accion": "guardar_borrador",
                },
            ).status_code,
            404,
        )
        novedad.refresh_from_db()
        self.assertEqual(novedad.descripcion_inicial, descripcion_original)

    def test_usuario_normal_no_elimina_novedad_finalizada(self):
        novedad = self.crear_registrada(usuario=self.usuario1)
        self.client.force_login(self.usuario1)
        url = reverse("bitaturno:eliminar_borrador", args=(novedad.pk,))

        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertTrue(Novedad.objects.filter(pk=novedad.pk).exists())

    def test_usuario_normal_puede_cambiar_solo_estado_segun_regla_actual(self):
        novedad = self.crear_registrada(usuario=self.usuario1)
        titulo_original = novedad.titulo
        descripcion_original = novedad.descripcion_inicial
        self.client.force_login(self.usuario1)

        respuesta = self.client.post(
            reverse("bitaturno:cambiar_estado", args=(novedad.pk,)),
            {"estado_operacional": Novedad.EstadoOperacional.CERRADA},
        )
        novedad.refresh_from_db()

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(
            novedad.estado_operacional,
            Novedad.EstadoOperacional.CERRADA,
        )
        self.assertEqual(novedad.titulo, titulo_original)
        self.assertEqual(novedad.descripcion_inicial, descripcion_original)

    def test_novedad_registrada_no_puede_eliminarse_desde_aplicacion(self):
        novedad = self.crear_registrada()
        self.client.force_login(self.usuario1)
        url = reverse("bitaturno:eliminar_borrador", args=(novedad.pk,))
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertTrue(Novedad.objects.filter(pk=novedad.pk).exists())

    def test_contadores_de_inicio(self):
        self.crear_registrada(titulo="Novedad pendiente")
        self.crear_registrada(
            titulo="Novedad en revisión",
            estado_operacional=Novedad.EstadoOperacional.EN_REVISION,
        )
        self.crear_registrada(
            titulo="Novedad cerrada",
            estado_operacional=Novedad.EstadoOperacional.CERRADA,
            fecha_cierre=timezone.now(),
        )
        self.crear_borrador()
        self.crear_borrador(usuario=self.usuario2)
        self.client.force_login(self.usuario1)
        respuesta = self.client.get(reverse("bitaturno:inicio"))
        self.assertEqual(respuesta.context["resumen"]["total_registradas"], 3)
        self.assertEqual(respuesta.context["resumen"]["pendientes"], 1)
        self.assertEqual(respuesta.context["resumen"]["en_revision"], 1)
        self.assertEqual(respuesta.context["resumen"]["cerradas"], 1)
        self.assertEqual(respuesta.context["resumen"]["mis_borradores"], 1)

    def test_catalogos_y_novedad_estan_registrados_en_admin(self):
        for modelo in (Disciplina, TipoNovedad, Turno, Area, Equipo, Novedad):
            with self.subTest(modelo=modelo.__name__):
                self.assertTrue(admin.site.is_registered(modelo))
