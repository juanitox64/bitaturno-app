from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify


MAXIMO_FOTOGRAFIA_ORIGINAL_BYTES = 25 * 1024 * 1024
MAXIMO_FOTOGRAFIA_ALMACENADA_BYTES = 3 * 1024 * 1024
MAXIMO_DIMENSION_FOTOGRAFIA = 2048
MINIMA_DIMENSION_FOTOGRAFIA = 640
CALIDADES_WEBP = (85, 82, 78, 74, 70)


def _nombre_webp(nombre_original):
    base = slugify(Path(nombre_original or "fotografia").stem)[:60]
    return f"{base or 'fotografia'}.webp"


def _preparar_imagen(archivo):
    try:
        archivo.seek(0)
        with Image.open(archivo) as original:
            imagen = ImageOps.exif_transpose(original)
            imagen.load()
            tiene_transparencia = imagen.mode in ("RGBA", "LA") or (
                imagen.mode == "P" and "transparency" in imagen.info
            )
            imagen = imagen.convert("RGBA" if tiene_transparencia else "RGB")
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as error:
        raise ValidationError(
            "No fue posible procesar la fotografía. Use una imagen JPEG, PNG o WEBP válida."
        ) from error
    finally:
        try:
            archivo.seek(0)
        except (AttributeError, OSError):
            pass

    imagen.thumbnail(
        (MAXIMO_DIMENSION_FOTOGRAFIA, MAXIMO_DIMENSION_FOTOGRAFIA),
        Image.Resampling.LANCZOS,
    )
    return imagen


def _codificar_webp(imagen, calidad):
    salida = BytesIO()
    imagen.save(
        salida,
        format="WEBP",
        quality=calidad,
        method=4,
        optimize=True,
    )
    return salida.getvalue()


def optimizar_fotografia(archivo):
    """Normaliza una fotografía, elimina metadatos y devuelve un WEBP de hasta 3 MB."""
    if archivo.size > MAXIMO_FOTOGRAFIA_ORIGINAL_BYTES:
        raise ValidationError("La fotografía original no puede superar 25 MB.")

    imagen = _preparar_imagen(archivo)
    ultimo_resultado = b""

    while True:
        for calidad in CALIDADES_WEBP:
            ultimo_resultado = _codificar_webp(imagen, calidad)
            if len(ultimo_resultado) <= MAXIMO_FOTOGRAFIA_ALMACENADA_BYTES:
                optimizada = SimpleUploadedFile(
                    _nombre_webp(getattr(archivo, "name", "fotografia")),
                    ultimo_resultado,
                    content_type="image/webp",
                )
                optimizada._bitaturno_optimizada = True
                return optimizada

        dimension_mayor = max(imagen.size)
        if dimension_mayor <= MINIMA_DIMENSION_FOTOGRAFIA:
            break

        factor = max(
            0.75,
            min(
                0.88,
                (
                    MAXIMO_FOTOGRAFIA_ALMACENADA_BYTES
                    / max(len(ultimo_resultado), 1)
                )
                ** 0.5
                * 0.95,
            ),
        )
        nuevo_tamano = (
            max(1, round(imagen.width * factor)),
            max(1, round(imagen.height * factor)),
        )
        imagen = imagen.resize(nuevo_tamano, Image.Resampling.LANCZOS)

    raise ValidationError(
        "No fue posible reducir la fotografía a un tamaño seguro. "
        "Intente con otra imagen."
    )
