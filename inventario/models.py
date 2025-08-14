import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from cloudinary_storage.storage import RawMediaCloudinaryStorage

class Proveedor(models.Model):
    nombre = models.CharField('Nombre', max_length=150, unique=True)
    email = models.EmailField('Correo', blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True, null=True)
    notas = models.TextField('Notas', blank=True, null=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class TipoProducto(models.TextChoices):
        NUEVO = 'Nuevo', 'Nuevo'
        REPUESTO = 'Repuesto', 'Repuesto'
        SERVICIO = 'Servicio', 'Servicio'
        KIT = 'Kit', 'Kit'

    class Estado(models.TextChoices):
        DISPONIBLE = 'Disponible', 'Disponible'
        RESERVADO = 'Reservado', 'Reservado'
        VENDIDO = 'Vendido', 'Vendido'
        DANADO = 'Dañado', 'Dañado'
        DESECHADO = 'Desechado', 'Desechado'

    class UnidadMedida(models.TextChoices):
        PZA = 'pza', 'Pieza'
        SET = 'set', 'Set'
        KG = 'kg', 'Kg'
        HORA = 'unidad_hora', 'Unidad/Hora'

    class VisibilidadOnline(models.TextChoices):
        OCULTO = 'Oculto', 'Oculto'
        CATALOGO = 'Catálogo', 'Catálogo'
        VENTA = 'Venta', 'Venta'

    internal_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    codigo_identificador = models.CharField(
        'Código identificador (QR o barra)', max_length=128, blank=True, null=True, unique=True
    )

    sku = models.CharField('SKU', max_length=64, unique=True)
    sku_proveedor = models.CharField('SKU proveedor', max_length=64, unique=True)

    nombre = models.CharField('Nombre', max_length=150)
    tipo_producto = models.CharField('Tipo de producto', max_length=20, choices=TipoProducto.choices)
    descripcion_corta = models.TextField('Descripción corta')
    palabras_clave = models.TextField('Palabras clave', blank=True, null=True)

    estado = models.CharField('Estado', max_length=20, choices=Estado.choices, default=Estado.DISPONIBLE)

    ubicacion_principal = models.CharField('Ubicación principal', max_length=100)
    cantidad_inicial = models.IntegerField('Cantidad inicial', default=0)
    stock_actual = models.IntegerField('Stock actual', default=0)
    unidad_medida = models.CharField('Unidad de medida', max_length=20, choices=UnidadMedida.choices)

    costo_unitario = models.DecimalField('Costo unitario', max_digits=12, decimal_places=2, blank=True, null=True)

    proveedor_principal = models.ForeignKey(
        Proveedor, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Proveedor principal'
    )

    fecha_alta = models.DateTimeField('Fecha de alta', default=timezone.now, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_creados'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_actualizados'
    )

    marca_fabricante = models.CharField('Marca fabricante', max_length=100, blank=True, null=True)
    modelo_fabricante = models.CharField('Modelo fabricante', max_length=100, blank=True, null=True)
    compatible_con_modelos = models.TextField('Compatible con modelos', blank=True, null=True)

    manual_tecnico_pdf = models.FileField(
        'Manual técnico (PDF)', upload_to='manuales/', storage=RawMediaCloudinaryStorage(),
        blank=True, null=True
    )

    precio_publico = models.DecimalField('Precio público', max_digits=12, decimal_places=2, blank=True, null=True)
    precio_oferta = models.DecimalField('Precio oferta', max_digits=12, decimal_places=2, blank=True, null=True)
    oferta_inicio = models.DateTimeField('Oferta inicio', blank=True, null=True)
    oferta_fin = models.DateTimeField('Oferta fin', blank=True, null=True)
    visibilidad_online = models.CharField(
        'Visibilidad online', max_length=20, choices=VisibilidadOnline.choices, default=VisibilidadOnline.OCULTO
    )
    peso_kg = models.DecimalField('Peso (kg)', max_digits=8, decimal_places=3, blank=True, null=True)
    largo_mm = models.IntegerField('Largo (mm)', blank=True, null=True)
    ancho_mm = models.IntegerField('Ancho (mm)', blank=True, null=True)
    alto_mm = models.IntegerField('Alto (mm)', blank=True, null=True)

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['sku_proveedor']),
            models.Index(fields=['nombre']),
            models.Index(fields=['codigo_identificador']),
        ]

    def __str__(self):
        return f"{self.nombre} [{self.sku}]"

    def agregar_stock(self, cantidad, usuario=None, ip=None, motivo='Ingreso'):
        MovimientoStock.registrar(self, cantidad, MovimientoStock.TipoMovimiento.ENTRADA, usuario, ip, motivo)

    def retirar_stock(self, cantidad, usuario=None, ip=None, motivo='Salida'):
        MovimientoStock.registrar(self, -abs(cantidad), MovimientoStock.TipoMovimiento.SALIDA, usuario, ip, motivo)


def imagen_upload_to(instance, filename):
    ext = (filename.rsplit('.', 1)[-1] or 'jpg').lower()
    return f"products/{instance.producto.internal_id}/{instance.secuencia}.{ext}"


class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to=imagen_upload_to)
    secuencia = models.PositiveSmallIntegerField('Secuencia', default=1)

    class Meta:
        verbose_name = 'Imagen de producto'
        verbose_name_plural = 'Imágenes de producto'
        unique_together = [('producto', 'secuencia')]

    def __str__(self):
        return f"{self.producto} img#{self.secuencia}"


class MovimientoStock(models.Model):
    class TipoMovimiento(models.TextChoices):
        ENTRADA = 'IN', 'Entrada'
        SALIDA = 'OUT', 'Salida'
        AJUSTE = 'ADJ', 'Ajuste'

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=3, choices=TipoMovimiento.choices)
    cantidad = models.IntegerField('Cantidad (signed)')
    motivo = models.CharField('Motivo', max_length=200, blank=True, null=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip = models.GenericIPAddressField('IP', blank=True, null=True)
    creado_en = models.DateTimeField('Creado en', auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de stock'
        verbose_name_plural = 'Movimientos de stock'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.get_tipo_display()} {self.cantidad} -> {self.producto}"

    @classmethod
    def registrar(cls, producto, cantidad_signed, tipo, usuario=None, ip=None, motivo=None):
        mv = cls.objects.create(
            producto=producto,
            tipo=tipo,
            cantidad=cantidad_signed,
            motivo=motivo,
            usuario=usuario,
            ip=ip,
        )
        producto.stock_actual = (producto.stock_actual or 0) + cantidad_signed
        producto.save(update_fields=['stock_actual', 'updated_at'])
        return mv