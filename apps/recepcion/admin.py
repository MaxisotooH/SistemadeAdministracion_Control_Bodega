from django.contrib import admin

from .models import Recepcion, RecepcionDetalle


class RecepcionDetalleInline(admin.TabularInline):
    model = RecepcionDetalle
    extra = 1
    can_delete = False


@admin.register(Recepcion)
class RecepcionAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha', 'numero_documento', 'registrado_por')
    list_filter = ('proveedor',)
    search_fields = ('numero_documento', 'proveedor__razon_social')
    inlines = [RecepcionDetalleInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.registrado_por_id:
            obj.registrado_por = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        # Eliminar una recepcion no revierte el Stock ni el Kardex ya
        # generados (no hay signal de post_delete): una vez registrada,
        # se deja como historial protegido, igual que el Kardex.
        return False
