# C:\Users\acant\Documents\XPYME\colaboradores\urls.py

from django.urls import path
from .views import ColaboradorListView, ColaboradorUpdateView

app_name = 'colaboradores'

urlpatterns = [
    path('', ColaboradorListView.as_view(), name='list'),
    path('<int:pk>/editar/', ColaboradorUpdateView.as_view(), name='editar'),
]