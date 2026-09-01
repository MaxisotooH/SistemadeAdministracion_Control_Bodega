from django.db import models

from apps.core.models import TimeStampedModel


class UnidadMedida(TimeStampedModel):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Unidad de medida'
        verbose_name_plural = 'Unidades de medida'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'


class Categoria(TimeStampedModel):
    nombre = models.CharField(max_length=100, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Marca(TimeStampedModel):
    nombre = models.CharField(max_length=100, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Proveedor(TimeStampedModel):
    razon_social = models.CharField(max_length=150)
    rut = models.CharField(max_length=20, unique=True)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']

    def __str__(self):
        return self.razon_social


class Cliente(TimeStampedModel):
    razon_social = models.CharField(max_length=150)
    rut = models.CharField(max_length=20, unique=True)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['razon_social']

    def __str__(self):
        return self.razon_social


class Bodega(TimeStampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'


class Zona(TimeStampedModel):
    bodega = models.ForeignKey(Bodega, on_delete=models.PROTECT, related_name='zonas')
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Zonas'
        ordering = ['bodega', 'codigo']
        unique_together = ('bodega', 'codigo')

    def __str__(self):
        return f'{self.bodega.codigo} / {self.codigo}'


class Ubicacion(TimeStampedModel):
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT, related_name='ubicaciones')
    codigo = models.CharField(max_length=30, help_text='Ej: pasillo-estante-nivel')
    capacidad = models.PositiveIntegerField(default=0, help_text='0 = sin límite definido')
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Ubicaciones'
        ordering = ['zona', 'codigo']
        unique_together = ('zona', 'codigo')

    def __str__(self):
        return f'{self.zona} / {self.codigo}'


class Producto(TimeStampedModel):
    sku = models.CharField(max_length=30, unique=True)
    codigo_barras = models.CharField(max_length=50, blank=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='productos', null=True, blank=True)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, related_name='productos')
    stock_minimo = models.PositiveIntegerField(default=0)
    stock_maximo = models.PositiveIntegerField(default=0)
    punto_reposicion = models.PositiveIntegerField(default=0)
    maneja_lote = models.BooleanField(default=False)
    maneja_serie = models.BooleanField(default=False)
    maneja_vencimiento = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.sku} - {self.nombre}'
