# Sistema de Administración y Control de Bodega

Sistema web para gestionar de forma integral la operación de una bodega:
ingreso y recepción de productos, almacenamiento y control de inventario,
movimientos internos, picking y despacho, devoluciones, ajustes, inventarios
físicos, trazabilidad, reportes y control de usuarios.

## Stack tecnológico

- **Backend:** Python 3.11+ / Django 5
- **Base de datos:** PostgreSQL
- **Frontend:** Plantillas Django (Jinja-like) + Bootstrap 5
- **Control de versiones:** Git / GitHub

## Estructura del repositorio

```
.
├── apps/                  # Apps de Django, una por módulo funcional
│   └── core/               # Dashboard, login, utilidades transversales
├── config/                 # Configuración del proyecto (settings, urls, wsgi/asgi)
├── docs/                    # Documentación de respaldo (funcional, Gantt, modelo de datos)
├── media/                   # Archivos subidos por usuarios (no versionado)
├── static/                  # CSS, JS e imágenes propias
│   ├── css/
│   ├── js/
│   └── img/
├── templates/                # Plantillas HTML (base.html + por app)
├── .env.example              # Variables de entorno de referencia
├── manage.py
└── requirements.txt
```

A medida que se desarrolle cada módulo del documento funcional (Maestros,
Compras, Recepción, Almacenamiento, Picking, Despacho, Kardex, etc.) se irá
agregando su app correspondiente dentro de `apps/`, con su propio
`models.py`, `views.py`, `urls.py` y templates.

## Puesta en marcha (desarrollo local)

1. Crear y activar un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Copiar variables de entorno y ajustar según tu entorno local:
   ```bash
   cp .env.example .env
   ```
4. Crear la base de datos PostgreSQL indicada en `DATABASE_URL` (o ajustar
   la URL a tu configuración).
5. Aplicar migraciones y crear un superusuario:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
6. Levantar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

## Estado del proyecto

Repositorio inicializado con la estructura base del proyecto. El análisis
del documento funcional y la Carta Gantt (fases, dependencias, horas
estimadas, hitos y alcance del MVP) se están trabajando por separado antes
de comenzar el desarrollo módulo por módulo.
