from axes.apps import AppConfig as AxesAppConfig


class AxesConfigEs(AxesAppConfig):
    """Igual que axes.apps.AppConfig, solo que con el nombre de la
    seccion del admin en español ('Axes' se ve raro para alguien que no
    conoce la libreria)."""
    verbose_name = 'Seguridad de acceso'
