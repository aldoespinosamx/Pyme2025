# C:\Users\acant\Documents\XPYME\inventario\urls.py

from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.SeleccionView.as_view(), name='seleccion'),
    path('buscar/', views.ProductoBuscarView.as_view(), name='buscar'),
    path('nuevo/', views.ProductoCrearView.as_view(), name='nuevo'),
    path('<uuid:internal_id>/editar/', views.ProductoEditarView.as_view(), name='editar'),
    path('<uuid:internal_id>/imagenes/', views.ProductoImagenesView.as_view(), name='imagenes'),
    path('<uuid:internal_id>/ajuste/', views.AjusteStockView.as_view(), name='ajuste'),
    path('scan/result/', views.ScanResultView.as_view(), name='scan_result'),
]