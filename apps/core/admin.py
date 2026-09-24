from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User

from axes.conf import settings as axes_settings
from axes.handlers.database import AxesDatabaseHandler
from axes.models import AccessAttempt, AccessFailureLog, AccessLog


# Los selectores de permisos/grupos (doble lista) quedan muy angostos con
# el CSS base de Django y cortan el texto -- se ensancha con un CSS propio,
# sin reemplazar el UserAdmin/GroupAdmin de Django (se reutiliza tal cual,
# solo se le agrega esta hoja de estilos).
class _AnchoExtraMixin:
    class Media:
        css = {'all': ('css/admin_extra.css',)}


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdminAncho(_AnchoExtraMixin, UserAdmin):
    pass


@admin.register(Group)
class GroupAdminAncho(_AnchoExtraMixin, GroupAdmin):
    pass

# django-axes no trae traduccion al español (revisar su carpeta locale/),
# asi que sus pantallas de administracion quedan en ingles por defecto.
# Se reemplazan aqui por versiones en español, mas simples de usar para
# alguien que no maneja este tipo de herramientas.
admin.site.unregister(AccessAttempt)
admin.site.unregister(AccessLog)
admin.site.unregister(AccessFailureLog)

# El nombre del modelo (titulo de pagina, conteo "N objetos", etc.) viene
# del verbose_name del modelo, no del ModelAdmin -- hay que cambiarlo aqui
# directamente porque el modelo pertenece a la libreria de axes.
AccessAttempt._meta.verbose_name = 'intento de acceso'
AccessAttempt._meta.verbose_name_plural = 'Intentos de acceso'
AccessLog._meta.verbose_name = 'registro de acceso'
AccessLog._meta.verbose_name_plural = 'Historial de accesos'
AccessFailureLog._meta.verbose_name = 'registro de fallo'
AccessFailureLog._meta.verbose_name_plural = 'Registros de fallos'

# Los filtros de la lista (list_filter) toman su titulo del verbose_name
# del campo del modelo, no del ModelAdmin -- se traducen aqui tambien.
AccessAttempt._meta.get_field('attempt_time').verbose_name = 'fecha del intento'
AccessLog._meta.get_field('attempt_time').verbose_name = 'fecha de ingreso'
AccessLog._meta.get_field('logout_time').verbose_name = 'fecha de salida'
AccessFailureLog._meta.get_field('attempt_time').verbose_name = 'fecha del intento'
AccessFailureLog._meta.get_field('locked_out').verbose_name = 'bloqueado'


class BloqueadoFiltro(admin.SimpleListFilter):
    title = 'bloqueado'
    parameter_name = 'bloqueado'

    def lookups(self, request, model_admin):
        return (('si', 'Sí'), ('no', 'No'))

    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.filter(failures_since_start__gte=axes_settings.AXES_FAILURE_LIMIT)
        if self.value() == 'no':
            return queryset.filter(failures_since_start__lt=axes_settings.AXES_FAILURE_LIMIT)
        return queryset


@admin.register(AccessAttempt)
class AccessAttemptAdminEs(admin.ModelAdmin):
    list_display = ('fecha', 'ip', 'usuario', 'ruta', 'intentos_fallidos', 'estado')
    list_filter = ('attempt_time', BloqueadoFiltro)
    search_fields = ('ip_address', 'username', 'user_agent', 'path_info')
    date_hierarchy = 'attempt_time'
    actions = ['desbloquear_seleccionados']

    fieldsets = (
        (None, {'fields': ('username', 'path_info', 'failures_since_start')}),
        ('Datos del formulario', {'fields': ('get_data', 'post_data')}),
        ('Datos técnicos', {'fields': ('user_agent', 'ip_address', 'http_accept')}),
    )
    readonly_fields = (
        'user_agent', 'ip_address', 'username', 'http_accept', 'path_info',
        'attempt_time', 'get_data', 'post_data', 'failures_since_start',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = AxesDatabaseHandler()

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        # Se oculta el "Eliminar" generico de Django: borrar un intento
        # de acceso ES desbloquear, asi que solo se deja esa opcion
        # (mas clara) para no confundir con dos acciones que hacen lo
        # mismo.
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    @admin.display(description='Fecha y hora')
    def fecha(self, obj):
        return obj.attempt_time

    @admin.display(description='Dirección IP')
    def ip(self, obj):
        return obj.ip_address

    @admin.display(description='Usuario')
    def usuario(self, obj):
        return obj.username

    @admin.display(description='Página')
    def ruta(self, obj):
        return obj.path_info

    @admin.display(description='Intentos fallidos')
    def intentos_fallidos(self, obj):
        return obj.failures_since_start

    @admin.display(description='Estado')
    def estado(self, obj):
        if obj.failures_since_start < axes_settings.AXES_FAILURE_LIMIT:
            restantes = axes_settings.AXES_FAILURE_LIMIT - obj.failures_since_start
            return f'{restantes} intento(s) restante(s)'
        return 'Bloqueado'

    @admin.action(description='Desbloquear usuario(s) seleccionado(s)')
    def desbloquear_seleccionados(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} usuario(s) desbloqueado(s) correctamente.')


@admin.register(AccessLog)
class AccessLogAdminEs(admin.ModelAdmin):
    list_display = ('fecha_ingreso', 'fecha_salida', 'ip', 'usuario', 'ruta')
    list_filter = ('attempt_time', 'logout_time')
    search_fields = ('ip_address', 'user_agent', 'username', 'path_info')
    date_hierarchy = 'attempt_time'

    fieldsets = (
        (None, {'fields': ('username', 'path_info')}),
        ('Datos técnicos', {'fields': ('user_agent', 'ip_address', 'http_accept')}),
    )
    readonly_fields = (
        'user_agent', 'ip_address', 'username', 'http_accept', 'path_info',
        'attempt_time', 'logout_time',
    )

    def has_add_permission(self, request):
        return False

    @admin.display(description='Ingreso')
    def fecha_ingreso(self, obj):
        return obj.attempt_time

    @admin.display(description='Salida')
    def fecha_salida(self, obj):
        return obj.logout_time

    @admin.display(description='Dirección IP')
    def ip(self, obj):
        return obj.ip_address

    @admin.display(description='Usuario')
    def usuario(self, obj):
        return obj.username

    @admin.display(description='Página')
    def ruta(self, obj):
        return obj.path_info


@admin.register(AccessFailureLog)
class AccessFailureLogAdminEs(admin.ModelAdmin):
    list_display = ('fecha', 'ip', 'usuario', 'ruta', 'bloqueado')
    list_filter = ('attempt_time', 'locked_out')
    search_fields = ('ip_address', 'user_agent', 'username', 'path_info')
    date_hierarchy = 'attempt_time'

    fieldsets = (
        (None, {'fields': ('username', 'path_info')}),
        ('Datos técnicos', {'fields': ('user_agent', 'ip_address', 'http_accept')}),
    )
    readonly_fields = (
        'user_agent', 'ip_address', 'username', 'http_accept', 'path_info',
        'attempt_time', 'locked_out',
    )

    def has_add_permission(self, request):
        return False

    @admin.display(description='Fecha y hora')
    def fecha(self, obj):
        return obj.attempt_time

    @admin.display(description='Dirección IP')
    def ip(self, obj):
        return obj.ip_address

    @admin.display(description='Usuario')
    def usuario(self, obj):
        return obj.username

    @admin.display(description='Página')
    def ruta(self, obj):
        return obj.path_info

    @admin.display(description='¿Bloqueado?', boolean=True)
    def bloqueado(self, obj):
        return obj.locked_out
