from django.contrib import admin

from .models import Kardex, Stock


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'ubicacion', 'lote', 'cantidad', 'fecha_vencimiento')
    list_filter = ('ubicacion__zona__bodega', 'producto__categoria')
    search_fields = ('producto__sku', 'producto__nombre', 'lote')


@admin.register(Kardex)
class KardexAdmin(admin.ModelAdmin):
    list_display = (
        'creado_en', 'tipo', 'producto', 'ubicacion', 'cantidad',
        'stock_anterior', 'stock_resultante', 'documento', 'usuario',
    )
    list_filter = ('tipo', 'ubicacion__zona__bodega')
    search_fields = ('producto__sku', 'producto__nombre', 'documento')
    date_hierarchy = 'creado_en'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
