"""
Configuración de Django para el proyecto Sistema de Administración
y Control de Bodega.
"""
from pathlib import Path
import environ

# ---------------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Variables de entorno (ver .env.example)
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
)
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)

SECRET_KEY = env('DJANGO_SECRET_KEY', default='dev-insecure-secret-key-change-me')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# ---------------------------------------------------------------------------
# Monitoreo de errores (Sentry). Se activa solo si SENTRY_DSN esta
# configurado en .env -- sin eso, no hace nada (no rompe el desarrollo
# local). El DSN se obtiene creando una cuenta gratuita en sentry.io.
# ---------------------------------------------------------------------------
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # Porcentaje de requests normales a rastrear para medir rendimiento.
        # Bajo a proposito: el objetivo principal es enterarse de errores,
        # no pagar por trazas de cada clic.
        traces_sample_rate=0.1,
        # No manda nombre/usuario/IP salvo que se active a proposito --
        # cuida la privacidad de quien esta usando el sistema.
        send_default_pii=False,
        environment=env('SENTRY_ENVIRONMENT', default='development'),
    )

# ---------------------------------------------------------------------------
# Aplicaciones instaladas
# ---------------------------------------------------------------------------
# 'jazzmin' le da al admin de Django una apariencia moderna y amigable
# (iconos, sidebar, temas) -- debe ir ANTES que 'django.contrib.admin'
# para poder reemplazar sus plantillas.
DJANGO_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Apps propias del sistema de bodega. Se van habilitando a medida que
# se desarrolla cada módulo (ver Carta Gantt / Fases del documento
# funcional). 'core' agrupa utilidades transversales (dashboard,
# autenticación, permisos base).
LOCAL_APPS = [
    'apps.core',
    'apps.maestros',
    'apps.inventario',
    'apps.recepcion',
    'apps.despacho',
    # 'apps.usuarios',
    # 'apps.compras',
]

# 'axes' controla el bloqueo de cuentas tras varios intentos de login
# fallidos (ver AXES_* mas abajo). Se usa una subclase propia de su
# AppConfig solo para que la seccion del admin diga "Seguridad de
# acceso" en vez de "Axes".
THIRD_PARTY_APPS = [
    'apps.core.axes_config.AxesConfigEs',
]

# THIRD_PARTY_APPS va antes que LOCAL_APPS: apps/core/admin.py reemplaza
# el admin de 'axes' por uno en español, y para eso 'axes' debe registrar
# el suyo primero (el autodiscovery de admin sigue el orden de esta lista).
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Debe ser el ultimo middleware (lo exige django-axes).
    'axes.middleware.AxesMiddleware',
]

# ---------------------------------------------------------------------------
# Bloqueo de cuenta tras intentos fallidos (django-axes)
# ---------------------------------------------------------------------------
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # horas
AXES_LOCKOUT_TEMPLATE = '403_bloqueado.html'
AXES_RESET_ON_SUCCESS = True

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------------------
# Base de datos (PostgreSQL)
# ---------------------------------------------------------------------------
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='postgres://bodega_user:bodega_pass@localhost:5432/bodega_db',
    )
}

# ---------------------------------------------------------------------------
# Validación de contraseñas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Archivos estáticos y de medios
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        # El manifiesto con hash (cache-busting) solo tiene sentido tras un
        # collectstatic real en produccion; en dev/tests no existe y
        # ManifestStaticFilesStorage revienta con "Missing staticfiles
        # manifest entry" en cualquier template que use {% static %}.
        'BACKEND': (
            'whitenoise.storage.CompressedManifestStaticFilesStorage'
            if not DEBUG else
            'django.contrib.staticfiles.storage.StaticFilesStorage'
        ),
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

CSRF_FAILURE_VIEW = 'apps.core.views.csrf_failure'

# ---------------------------------------------------------------------------
# Apariencia del admin (django-jazzmin): pensado para gente que no usa
# este tipo de herramientas a diario -- iconos claros por seccion, colores
# suaves y textos en español, en vez del admin tecnico por defecto.
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    'site_title': 'Bodega',
    'site_header': 'Bodega',
    'site_brand': 'Sistema de Bodega',
    'welcome_sign': 'Bienvenido al sistema de administración de bodega',
    'copyright': 'Sistema de Administración y Control de Bodega',
    'show_sidebar': True,
    'navigation_expanded': True,
    'search_model': ['maestros.Producto', 'maestros.Cliente', 'maestros.Proveedor'],
    'icons': {
        'auth.Group': 'fas fa-users-cog',
        'auth.User': 'fas fa-user',
        'maestros.Producto': 'fas fa-box',
        'maestros.Categoria': 'fas fa-tags',
        'maestros.Marca': 'fas fa-certificate',
        'maestros.UnidadMedida': 'fas fa-ruler',
        'maestros.Proveedor': 'fas fa-truck',
        'maestros.Cliente': 'fas fa-user-tie',
        'maestros.Bodega': 'fas fa-warehouse',
        'maestros.Zona': 'fas fa-layer-group',
        'maestros.Ubicacion': 'fas fa-map-marker-alt',
        'inventario.Stock': 'fas fa-boxes',
        'inventario.Kardex': 'fas fa-history',
        'recepcion.Recepcion': 'fas fa-dolly',
        'despacho.Despacho': 'fas fa-shipping-fast',
    },
    'default_icon_parents': 'fas fa-folder',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': True,
    'show_ui_builder': False,
    'language_chooser': False,
    # 'custom_links' cuelga del menu lateral de una app -- como 'core' no
    # tiene modelos registrados en el admin, ese grupo nunca aparece y el
    # link se pierde. 'topmenu_links' en cambio va en la barra superior,
    # siempre visible sin depender de eso.
    'topmenu_links': [
        {'name': 'Volver al inicio', 'url': 'dashboard', 'icon': 'fas fa-home'},
    ],
}

JAZZMIN_UI_TWEAKS = {
    'theme': 'flatly',
    'navbar': 'navbar-white navbar-light',
    'sidebar': 'sidebar-light-primary',
    'brand_colour': 'navbar-primary',
    'accent': 'accent-primary',
    'navbar_fixed': True,
    'sidebar_fixed': True,
    'sidebar_nav_child_indent': True,
    'layout_boxed': False,
}

# ---------------------------------------------------------------------------
# Endurecimiento para produccion (solo aplica cuando DEBUG=False, para no
# interferir con el servidor de desarrollo local en HTTP).
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=60 * 60 * 24 * 30)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Necesario detras de un proxy/balanceador (Railway, Render, Heroku, etc.)
    # que termina TLS y reenvia la peticion por HTTP interno.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
