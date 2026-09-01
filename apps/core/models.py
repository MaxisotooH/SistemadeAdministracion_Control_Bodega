from django.db import models


class TimeStampedModel(models.Model):
    """
    Modelo abstracto base para auditoría mínima (creado/modificado).
    Todos los modelos del sistema (maestros, kardex, movimientos, etc.)
    deberían heredar de esta clase para mantener trazabilidad consistente.
    """
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
