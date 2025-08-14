from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from datetime import date
import datetime

from .models import CustomUser, Role

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'paternal_last_name', 'maternal_last_name',
            'email', 'phone', 'emergency_contact_name', 'emergency_contact_phone',
            'date_of_birth', 'date_of_joining', 'blood_type', 'nss', 'rfc',
            'base_salary', 'role_obj', 'password1', 'password2',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            min_allowed = datetime.date(today.year - 15, today.month, today.day)
            if dob > min_allowed:
                raise ValidationError('El usuario debe tener al menos 15 años.')
        return dob

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            if f.required:
                f.label = f"{f.label} *"


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        exclude = ('username', 'password')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            min_allowed = datetime.date(today.year - 15, today.month, today.day)
            if dob > min_allowed:
                raise ValidationError('El usuario debe tener al menos 15 años.')
        return dob

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            if f.required:
                f.label = f"{f.label} *"


class CustomUserChangeForm(UserChangeForm):
    """
    Para el admin de Django: incluye todos los campos.
    """
    class Meta:
        model = CustomUser
        fields = '__all__'