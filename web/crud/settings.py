import os
import secrets
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


def env_list(nombre, valor_predeterminado=""):
    return [
        valor.strip()
        for valor in os.environ.get(nombre, valor_predeterminado).split(",")
        if valor.strip()
    ]


DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        # Clave efímera para desarrollo local: evita publicar una clave fija.
        SECRET_KEY = secrets.token_urlsafe(50)
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY es obligatoria cuando DJANGO_DEBUG=0."
        )
ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost,testserver",
)
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.bitaturno.apps.BitaTurnoConfig",
    "apps.data_transfer.apps.DataTransferConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "crud.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "crud.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(
            os.environ.get("DJANGO_DB_PATH", str(BASE_DIR / "db.sqlite3"))
        ),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = Path(
    os.environ.get("DJANGO_STATIC_ROOT", str(BASE_DIR / "staticfiles"))
)
MEDIA_URL = "media/"
MEDIA_ROOT = Path(os.environ.get("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media")))
DATA_TRANSFER_MAX_PACKAGE_BYTES = int(
    os.environ.get("DATA_TRANSFER_MAX_PACKAGE_BYTES", 64 * 1024 * 1024)
)
DATA_TRANSFER_MAX_FILES = int(os.environ.get("DATA_TRANSFER_MAX_FILES", 500))
DATA_TRANSFER_MAX_UNCOMPRESSED_BYTES = int(
    os.environ.get("DATA_TRANSFER_MAX_UNCOMPRESSED_BYTES", 128 * 1024 * 1024)
)
DATA_TRANSFER_RETENTION = int(os.environ.get("DATA_TRANSFER_RETENTION", 10))
DATA_TRANSFER_WORK_ROOT = Path(
    os.environ.get(
        "DATA_TRANSFER_WORK_ROOT",
        str(DATABASES["default"]["NAME"].parent / "transferencias"),
    )
)
DATA_TRANSFER_UPLOAD_ROOT = DATA_TRANSFER_WORK_ROOT / "cargas"
DATA_TRANSFER_EXPORT_ROOT = DATA_TRANSFER_WORK_ROOT / "exportaciones"
DATA_TRANSFER_BACKUP_ROOT = DATA_TRANSFER_WORK_ROOT / "respaldos"

DATA_UPLOAD_MAX_MEMORY_SIZE = max(
    32 * 1024 * 1024,
    DATA_TRANSFER_MAX_PACKAGE_BYTES + 1024 * 1024,
)
# Los archivos mayores pasan a un temporal para no mantener originales grandes en RAM.
FILE_UPLOAD_MAX_MEMORY_SIZE = 4 * 1024 * 1024
FILE_UPLOAD_PERMISSIONS = 0o640
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o750

LOGIN_URL = "bitaturno:login"
LOGIN_REDIRECT_URL = "bitaturno:inicio"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
