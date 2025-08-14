from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from colaboradores.models import Colaborador

@admin.register(Colaborador)
class ColaboradorAdmin(UserAdmin):
    """
    Reutiliza la configuración de UserAdmin,
    pero deja username como solo lectura.
    """
    readonly_fields = ('username',)
    list_display = ('username', 'role_obj', 'phone')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información editable', {
            'fields': (
                'first_name', 'paternal_last_name', 'maternal_last_name',
                'email', 'phone', 'emergency_contact_name',
                'emergency_contact_phone', 'date_of_birth',
                'date_of_joining', 'blood_type', 'nss',
                'rfc', 'base_salary', 'role_obj'
            )
        }),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )