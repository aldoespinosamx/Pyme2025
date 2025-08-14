# C:\Users\acant\Documents\XPYME\inventario\admin.py

from django.contrib import admin
from .models import Producto, ImagenProducto, MovimientoStock, Proveedor

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 0

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'sku',
        'estado',
        'stock_actual',
        'ubicacion_principal',
    )
    search_fields = (
        'nombre',
        'sku',
        'sku_proveedor',
        'codigo_identificador',
        'palabras_clave',
    )
    list_filter = (
        'estado',
        'tipo_producto',
        'visibilidad_online',
    )
    inlines = [ImagenProductoInline]
    readonly_fields = (
        'internal_id',
        'fecha_alta',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'email',
        'telefono',
    )
    search_fields = ('nombre',)

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = (
        'producto',
        'tipo',
        'cantidad',
        'usuario',
        'ip',
        'creado_en',
    )
    search_fields = (
        'producto__nombre',
        'producto__sku',
        'usuario__username',
    )
    list_filter = ('tipo',)