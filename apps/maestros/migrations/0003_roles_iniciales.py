from django.db import migrations

PERFILES = {
    'Administrador': {
        'apps_crud': ['maestros', 'inventario', 'recepcion', 'despacho'],
    },
    'Jefe de Bodega': {
        'apps_crud': ['maestros', 'inventario', 'recepcion', 'despacho'],
    },
    'Operador de Bodega': {
        'apps_crud': ['recepcion', 'despacho'],
        'apps_vista': ['maestros', 'inventario'],
    },
    'Compras': {
        'apps_crud': ['recepcion'],
        'apps_vista': ['maestros'],
    },
    'Ventas': {
        'apps_crud': ['despacho'],
        'apps_vista': ['maestros'],
    },
    'Contabilidad (consulta)': {
        'apps_vista': ['maestros', 'inventario', 'recepcion', 'despacho'],
    },
    'Auditoria (consulta)': {
        'apps_vista': ['maestros', 'inventario', 'recepcion', 'despacho'],
    },
}


def crear_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    for nombre, config in PERFILES.items():
        grupo, _ = Group.objects.get_or_create(name=nombre)
        permisos = Permission.objects.none()

        for app_label in config.get('apps_crud', []):
            permisos |= Permission.objects.filter(
                content_type__app_label=app_label,
                codename__regex=r'^(add|change|delete|view)_',
            )

        for app_label in config.get('apps_vista', []):
            permisos |= Permission.objects.filter(
                content_type__app_label=app_label,
                codename__startswith='view_',
            )

        grupo.permissions.set(permisos)


def eliminar_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=PERFILES.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('maestros', '0002_alter_proveedor_options_alter_ubicacion_options'),
        ('inventario', '0001_initial'),
        ('recepcion', '0001_initial'),
        ('despacho', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_roles, eliminar_roles),
    ]
