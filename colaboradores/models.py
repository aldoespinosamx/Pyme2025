from django.contrib.auth import get_user_model
from django.db import models

CustomUser = get_user_model()

class Colaborador(CustomUser):
    """
    Proxy model para listar/editar usuarios en el directorio de Recursos Humanos.
    No añade columnas nuevas.
    """
    class Meta:
        proxy = True
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'