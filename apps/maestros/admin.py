from django.contrib import admin

from .models import (
    Bodega,
    Categoria,
    Cliente,
    Marca,
    Producto,
    Proveedor,
    UnidadMedida,
    Ubicacion,
    Zona,
)


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'rut', 'telefono', 'email', 'activo')
    list_filter = ('activo',)
    search_fields = ('razon_social', 'rut')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'rut', 'telefono', 'email', 'activo')
    list_filter = ('activo',)
    search_fields = ('razon_social', 'rut')


@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activa')
    list_filter = ('activa',)
    search_fields = ('codigo', 'nombre')


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ('bodega', 'codigo', 'nombre', 'activa')
    list_filter = ('bodega', 'activa')
    search_fields = ('codigo', 'nombre')


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('zona', 'codigo', 'capacidad', 'activa')
    list_filter = ('zona__bodega', 'activa')
    search_fields = ('codigo',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'sku', 'nombre', 'categoria', 'marca', 'unidad_medida',
        'stock_minimo', 'stock_maximo', 'activo',
    )
    list_filter = ('categoria', 'marca', 'activo', 'maneja_lote', 'maneja_serie', 'maneja_vencimiento')
    search_fields = ('sku', 'codigo_barras', 'nombre')
