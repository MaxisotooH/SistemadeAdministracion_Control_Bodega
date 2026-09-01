from django.apps import AppConfig


class RecepcionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.recepcion'
    label = 'recepcion'
    verbose_name = 'Recepción'

    def ready(self):
        from . import signals  # noqa: F401
