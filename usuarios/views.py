from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser

class UserCreateView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'usuarios/crear.html'
    success_url = reverse_lazy('usuarios:list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class UserListView(ListView):
    model = CustomUser
    template_name = 'usuarios/list.html'
    context_object_name = 'usuarios'


class UserUpdateView(UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'usuarios/editar.html'
    success_url = reverse_lazy('usuarios:list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)