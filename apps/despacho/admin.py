from django.contrib import admin

from .forms import DespachoDetalleBaseFormSet
from .models import Despacho, DespachoDetalle


class DespachoDetalleInline(admin.TabularInline):
    model = DespachoDetalle
    formset = DespachoDetalleBaseFormSet
    extra = 1


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'numero_documento', 'registrado_por')
    list_filter = ('cliente',)
    search_fields = ('numero_documento', 'cliente__razon_social')
    inlines = [DespachoDetalleInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.registrado_por_id:
            obj.registrado_por = request.user
        super().save_model(request, obj, form, change)
