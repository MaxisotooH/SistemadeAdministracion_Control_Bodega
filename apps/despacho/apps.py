from django.apps import AppConfig


class DespachoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.despacho'
    label = 'despacho'
    verbose_name = 'Despacho'

    def ready(self):
        from . import signals  # noqa: F401
