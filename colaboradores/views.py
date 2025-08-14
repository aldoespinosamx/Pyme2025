from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model

from .forms import ColaboradorUpdateForm

CustomUser = get_user_model()

class ColaboradorListView(ListView):
    model = CustomUser
    template_name = 'colaboradores/list.html'
    context_object_name = 'colaboradores'

class ColaboradorUpdateView(UpdateView):
    model = CustomUser
    form_class = ColaboradorUpdateForm
    template_name = 'colaboradores/editar.html'
    success_url = reverse_lazy('colaboradores:list')

    def form_valid(self, form):
        messages.success(self.request, 'Datos actualizados correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)