from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.forms import inlineformset_factory
from .models import Producto, ImagenProducto, Proveedor

MANAGEMENT_ROLES = {'Administrador', 'Supervisor', 'Boss'}
MAX_IMAGE_MB = 2  # límite recomendado por subida

def user_is_manager(user):
    try:
        return bool(user.is_superuser or (getattr(user, 'role_obj', None) and user.role_obj.name in MANAGEMENT_ROLES))
    except Exception:
        return bool(user.is_superuser)

class ProductoCreateForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'codigo_identificador',
            'sku', 'sku_proveedor', 'nombre', 'tipo_producto',
            'descripcion_corta', 'palabras_clave', 'estado',
            'ubicacion_principal', 'cantidad_inicial', 'unidad_medida',
            'costo_unitario',  # sensible
            'proveedor_principal',
            'marca_fabricante', 'modelo_fabricante', 'compatible_con_modelos',
            'manual_tecnico_pdf',
            # E-commerce (sensibles)
            'precio_publico', 'precio_oferta', 'oferta_inicio', 'oferta_fin',
            'visibilidad_online', 'peso_kg', 'largo_mm', 'ancho_mm', 'alto_mm',
        ]
        widgets = {
            'codigo_identificador': forms.TextInput(attrs={
                'readonly': 'readonly',
                'id': 'codigoInput',
                'placeholder': 'Escanea o escribe el código del producto'
            }),
            'oferta_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'oferta_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # oculta campos sensibles si el rol no corresponde
        if not self.user or not user_is_manager(self.user):
            for name in ['costo_unitario', 'precio_publico', 'precio_oferta',
                         'oferta_inicio', 'oferta_fin', 'visibilidad_online',
                         'peso_kg', 'largo_mm', 'ancho_mm', 'alto_mm']:
                self.fields.pop(name, None)

        # validadores PDF
        if 'manual_tecnico_pdf' in self.fields:
            self.fields['manual_tecnico_pdf'].validators.append(
                FileExtensionValidator(allowed_extensions=['pdf'])
            )

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo_producto')
        cant = cleaned.get('cantidad_inicial')
        if tipo != Producto.TipoProducto.SERVICIO:
            if cant is None:
                raise ValidationError('La cantidad inicial es obligatoria para tipos distintos a Servicio.')
        else:
            cleaned['cantidad_inicial'] = 0
        return cleaned


class ProductoUpdateForm(ProductoCreateForm):
    class Meta(ProductoCreateForm.Meta):
        exclude = ['internal_id']


class ImagenProductoForm(forms.ModelForm):
    class Meta:
        model = ImagenProducto
        fields = ['imagen', 'secuencia']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'accept': 'image/*', 'capture': 'environment'})
        }

    def clean_imagen(self):
        img = self.cleaned_data.get('imagen')
        if img and img.size > MAX_IMAGE_MB * 1024 * 1024:
            raise ValidationError(f'La imagen supera {MAX_IMAGE_MB}MB. Usa menor resolución o comprime.')
        return img


ImagenProductoFormSet = inlineformset_factory(
    parent_model=Producto,
    model=ImagenProducto,
    form=ImagenProductoForm,
    fields=['imagen', 'secuencia'],
    extra=4,
    max_num=4,
    can_delete=True
)


class AjusteStockForm(forms.Form):
    ACCION_CHOICES = [
        ('add', 'Agregar'),
        ('remove', 'Quitar'),
        ('adjust', 'Ajuste manual'),
    ]
    accion = forms.ChoiceField(choices=ACCION_CHOICES)
    cantidad = forms.IntegerField(min_value=1)
    motivo = forms.CharField(max_length=200, required=False)