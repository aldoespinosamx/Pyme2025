from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        'username', 'email', 'first_name', 'paternal_last_name',
        'phone', 'role_obj', 'is_staff'
    )
    search_fields = ('username', 'email', 'phone', 'first_name', 'paternal_last_name')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {
            'fields': (
                'first_name', 'paternal_last_name', 'maternal_last_name',
                'email', 'phone', 'emergency_contact_name', 'emergency_contact_phone',
                'date_of_birth', 'date_of_joining', 'blood_type',
                'nss', 'rfc', 'base_salary', 'role_obj'
            )
        }),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'paternal_last_name', 'maternal_last_name',
                'email', 'phone', 'emergency_contact_name', 'emergency_contact_phone',
                'date_of_birth', 'date_of_joining', 'blood_type',
                'nss', 'rfc', 'base_salary', 'role_obj',
                'password1', 'password2', 'is_active', 'is_staff'
            ),
        }),
    )