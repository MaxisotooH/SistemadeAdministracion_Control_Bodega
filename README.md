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

Se está construyendo el MVP definido en `docs/Carta Gantt - Sistema Bodega
MVP.docx` (4 semanas, 90 HH), que es un recorte del documento funcional
completo (`docs/Proyecto_Sistema_Administracion_Control_Bodega.docx`).

- ✅ Semana 1 (parcial): app `apps/maestros` con el DER simplificado
  (Producto, Categoría, Marca, Unidad de medida, Proveedor, Cliente,
  Bodega, Zona, Ubicación), administrable vía Django Admin.
- ⬜ Semana 1: roles y permisos (grupos de Django) para los perfiles del
  documento funcional.
- ⬜ Semana 2: Recepción/Almacenamiento y Kardex automático (signals).
- ⬜ Semana 3: Vista de inventario/stock disponible y Despacho.
- ⬜ Semana 4: Pruebas del ciclo completo e implementación del MVP.

Quedan fuera del MVP (documentados como Fase 2): devoluciones, ajustes de
inventario físico, dashboard valorizado, alertas, reportes/exportación y
auditoría avanzada.
