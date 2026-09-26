import glob
import os
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


def _buscar_pg_dump():
    """Encuentra pg_dump: primero en el PATH, y si no, en las rutas
    tipicas de instalacion de PostgreSQL en Windows."""
    encontrado = shutil.which('pg_dump')
    if encontrado:
        return encontrado

    candidatos = sorted(
        glob.glob(r'C:\Program Files\PostgreSQL\*\bin\pg_dump.exe'),
        reverse=True,  # la version mas alta primero
    )
    if candidatos:
        return candidatos[0]

    return None


class Command(BaseCommand):
    help = 'Crea un respaldo (.sql) de la base de datos PostgreSQL en backups/.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mantener-dias', type=int, default=14,
            help='Elimina respaldos mas antiguos que esta cantidad de dias (0 = no borrar ninguno).',
        )

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        if 'postgresql' not in db['ENGINE']:
            raise CommandError(
                'Este comando es solo para PostgreSQL. La base de datos actual es: '
                f'{db["ENGINE"]}'
            )

        pg_dump = _buscar_pg_dump()
        if not pg_dump:
            raise CommandError(
                'No se encontro pg_dump. Si PostgreSQL esta instalado, agrega su carpeta '
                r"bin (p.ej. C:\Program Files\PostgreSQL\17\bin) al PATH."
            )

        carpeta = Path(settings.BASE_DIR) / 'backups'
        carpeta.mkdir(exist_ok=True)

        marca_tiempo = datetime.now().strftime('%Y%m%d_%H%M%S')
        destino = carpeta / f'bodega_{marca_tiempo}.sql'

        env = os.environ.copy()
        if db.get('PASSWORD'):
            env['PGPASSWORD'] = db['PASSWORD']

        comando = [
            pg_dump,
            '-h', db.get('HOST') or 'localhost',
            '-p', str(db.get('PORT') or 5432),
            '-U', db['USER'],
            '-F', 'p',  # formato plano (.sql legible)
            '-f', str(destino),
            db['NAME'],
        ]

        inicio = time.time()
        resultado = subprocess.run(comando, env=env, capture_output=True, text=True)

        if resultado.returncode != 0:
            destino.unlink(missing_ok=True)
            raise CommandError(f'pg_dump fallo:\n{resultado.stderr}')

        duracion = time.time() - inicio
        tamano_mb = destino.stat().st_size / (1024 * 1024)
        self.stdout.write(self.style.SUCCESS(
            f'Respaldo creado: {destino} ({tamano_mb:.2f} MB, {duracion:.1f}s)'
        ))

        mantener_dias = options['mantener_dias']
        if mantener_dias > 0:
            limite = datetime.now() - timedelta(days=mantener_dias)
            eliminados = 0
            for archivo in carpeta.glob('bodega_*.sql'):
                if datetime.fromtimestamp(archivo.stat().st_mtime) < limite:
                    archivo.unlink()
                    eliminados += 1
            if eliminados:
                self.stdout.write(f'Se eliminaron {eliminados} respaldo(s) de más de {mantener_dias} días.')
