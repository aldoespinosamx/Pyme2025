# C:\Users\acant\Documents\XPYME\inventario\views.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, FormView

from .models import Producto, ImagenProducto, MovimientoStock
from .forms import (
    ProductoCreateForm, ProductoUpdateForm,
    ImagenProductoFormSet, AjusteStockForm
)

def client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

class SeleccionView(LoginRequiredMixin, TemplateView):
    template_name = 'inventario/seleccion.html'

class ProductoBuscarView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'inventario/buscar.html'
    context_object_name = 'productos'

    def get_queryset(self):
        q = self.request.GET.get('q', '').strip()
        qs = Producto.objects.all()
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(sku__icontains=q) |
                Q(sku_proveedor__icontains=q) |
                Q(codigo_identificador__icontains=q) |
                Q(palabras_clave__icontains=q)
            )
        return qs.order_by('nombre')

class ProductoCrearView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoCreateForm
    template_name = 'inventario/producto_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        code = self.request.GET.get('code')
        if code:
            initial = kwargs.get('initial', {})
            initial.setdefault('codigo_identificador', code)
            kwargs['initial'] = initial
        return kwargs

    def form_valid(self, form):
        producto = form.save(commit=False)
        producto.created_by = self.request.user
        producto.updated_by = self.request.user
        producto.stock_actual = form.cleaned_data.get('cantidad_inicial') or 0
        producto.save()
        form.save_m2m()

        cant = producto.cantidad_inicial or 0
        if cant > 0:
            MovimientoStock.registrar(
                producto=producto,
                cantidad_signed=cant,
                tipo=MovimientoStock.TipoMovimiento.ENTRADA,
                usuario=self.request.user,
                ip=client_ip(self.request),
                motivo='Alta de producto (inicial)'
            )
        messages.success(self.request, 'Producto creado correctamente.')
        return redirect('inventario:imagenes', internal_id=producto.internal_id)

class ProductoEditarView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoUpdateForm
    template_name = 'inventario/producto_form.html'
    slug_field = 'internal_id'
    slug_url_kwarg = 'internal_id'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        producto = form.save(commit=False)
        producto.updated_by = self.request.user
        producto.save()
        form.save_m2m()
        messages.success(self.request, 'Producto actualizado correctamente.')
        return redirect('inventario:editar', internal_id=producto.internal_id)

class ProductoImagenesView(LoginRequiredMixin, UpdateView):
    model = Producto
    fields = []
    template_name = 'inventario/imagenes.html'
    slug_field = 'internal_id'
    slug_url_kwarg = 'internal_id'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['formset'] = ImagenProductoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            ctx['formset'] = ImagenProductoFormSet(instance=self.object)
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = ImagenProductoFormSet(request.POST, request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Imágenes actualizadas.')
            return redirect('inventario:editar', internal_id=self.object.internal_id)
        return self.render_to_response(self.get_context_data())

class AjusteStockView(LoginRequiredMixin, FormView):
    template_name = 'inventario/ajuste_stock.html'
    form_class = AjusteStockForm

    def get_product(self):
        return get_object_or_404(Producto, internal_id=self.kwargs['internal_id'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['producto'] = self.get_product()
        return ctx

    def form_valid(self, form):
        producto = self.get_product()
        accion = form.cleaned_data['accion']
        cantidad = form.cleaned_data['cantidad']
        motivo = form.cleaned_data.get('motivo') or accion
        ip = client_ip(self.request)

        if accion == 'add':
            MovimientoStock.registrar(producto, cantidad, MovimientoStock.TipoMovimiento.ENTRADA,
                                      self.request.user, ip,
                                      motivo='Ingreso manual' if motivo == 'add' else motivo)
        elif accion == 'remove':
            MovimientoStock.registrar(producto, -cantidad, MovimientoStock.TipoMovimiento.SALIDA,
                                      self.request.user, ip,
                                      motivo='Salida manual' if motivo == 'remove' else motivo)
        else:
            MovimientoStock.registrar(producto, cantidad, MovimientoStock.TipoMovimiento.AJUSTE,
                                      self.request.user, ip, motivo=motivo)

        if (producto.stock_actual or 0) == 0:
            messages.warning(self.request, f'Atención: el stock del producto {producto} llegó a CERO.')

        messages.success(self.request, 'Movimiento de stock aplicado.')
        return redirect('inventario:editar', internal_id=producto.internal_id)

class ScanResultView(LoginRequiredMixin, TemplateView):
    template_name = 'inventario/scan_result.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        code = self.request.GET.get('code', '').strip()
        producto = None
        if code:
            producto = Producto.objects.filter(Q(codigo_identificador=code)).first()
        ctx['code'] = code
        ctx['producto'] = producto
        return ctx

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        code = request.POST.get('code')
        producto = Producto.objects.filter(Q(codigo_identificador=code)).first()

        if action == 'agregar_existencia' and producto:
            MovimientoStock.registrar(producto, 1, MovimientoStock.TipoMovimiento.ENTRADA,
                                      request.user, client_ip(request),
                                      motivo='Ingreso por escaneo')
            messages.success(request, 'Se agregó 1 unidad al stock.')
            return redirect('inventario:editar', internal_id=producto.internal_id)

        if action == 'actualizar_info' and producto:
            return redirect('inventario:editar', internal_id=producto.internal_id)

        if action == 'ajustar_stock' and producto:
            return redirect('inventario:ajuste', internal_id=producto.internal_id)

        if action == 'crear_nuevo':
            return redirect(f"{reverse('inventario:nuevo')}?code={code}")

        return redirect('inventario:seleccion')