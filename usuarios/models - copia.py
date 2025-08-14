from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class Role(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nombre del rol'
    )
    permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Permisos adicionales',
        blank=True
    )

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    role_obj = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Rol',
        help_text='Rol vinculado al modelo Role'
    )

    first_name = models.CharField(
        'Nombre',
        max_length=150
    )
    paternal_last_name = models.CharField(
        'Apellido paterno',
        max_length=150
    )
    maternal_last_name = models.CharField(
        'Apellido materno',
        max_length=150,
        blank=True
    )

    email = models.EmailField(
        'Correo electrónico',
        unique=True
    )

    phone = models.CharField(
        'Teléfono',
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(r'^\d{10}$', 'El teléfono debe tener 10 dígitos.')
        ]
    )

    emergency_contact_name = models.CharField(
        'Nombre contacto emergencia',
        max_length=150,
        blank=True
    )
    emergency_contact_phone = models.CharField(
        'Teléfono contacto emergencia',
        max_length=10,
        blank=True,
        validators=[
            RegexValidator(r'^\d{10}$', 'El teléfono de emergencia debe tener 10 dígitos.')
        ]
    )

    date_of_birth = models.DateField(
        'Fecha de nacimiento',
        null=True,
        blank=True
    )
    date_of_joining = models.DateField(
        'Fecha de ingreso',
        blank=True,
        null=True
    )

    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    blood_type = models.CharField(
        'Tipo de sangre',
        max_length=3,
        choices=BLOOD_TYPE_CHOICES,
        blank=True,
        null=True
    )

    nss = models.CharField(
        'NSS',
        max_length=11,
        blank=True,
        validators=[
            RegexValidator(r'^\d{11}$', 'El NSS debe tener 11 dígitos.')
        ]
    )

    rfc = models.CharField(
        'RFC',
        max_length=13,
        validators=[
            RegexValidator(
                r'^[A-Za-zÑ&]{4}\d{6}[A-Za-z0-9]{3}$',
                'Formato de RFC inválido.'
            )
        ]
    )

    base_salary = models.DecimalField(
        'Sueldo base',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        'Fecha y hora de creación',
        default=timezone.now,
        editable=False
    )

    def save(self, *args, **kwargs):
        # Convertir RFC a mayúsculas antes de guardar
        self.rfc = self.rfc.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        label = f"{self.username}"
        if self.role_obj:
            label += f" ({self.role_obj.name})"
        return label