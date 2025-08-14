from django.urls import path
from .views import UserCreateView, UserListView, UserUpdateView

app_name = 'usuarios'

urlpatterns = [
    path('', UserListView.as_view(), name='list'),
    path('crear/', UserCreateView.as_view(), name='crear'),
    path('<int:pk>/editar/', UserUpdateView.as_view(), name='editar'),
]