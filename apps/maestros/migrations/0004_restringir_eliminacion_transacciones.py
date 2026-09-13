from django.db import migrations

PERMISOS_A_REMOVER = [
    ('recepcion', 'delete_recepcion'),
    ('recepcion', 'delete_recepciondetalle'),
    ('despacho', 'delete_despacho'),
    ('despacho', 'delete_despachodetalle'),
]


def restringir(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    permisos = Permission.objects.filter(
        content_type__app_label__in={app for app, _ in PERMISOS_A_REMOVER},
        codename__in=[codename for _, codename in PERMISOS_A_REMOVER],
    )
    for grupo in Group.objects.all():
        grupo.permissions.remove(*permisos)


def revertir(apps, schema_editor):
    # No se restauran automaticamente: el borrado de Recepcion/Despacho
    # queda deshabilitado a nivel de codigo (ver admin.py) porque no
    # revierte Stock/Kardex, asi que no tiene sentido re-otorgar el
    # permiso salvo que ese comportamiento cambie explicitamente.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('maestros', '0003_roles_iniciales'),
    ]

    operations = [
        migrations.RunPython(restringir, revertir),
    ]
