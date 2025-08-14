from django import forms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class ColaboradorUpdateForm(forms.ModelForm):
    """
    Formulario para editar todos los campos de un colaborador
    excepto username y password.
    """
    class Meta:
        model = CustomUser
        exclude = ('username', 'password')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marcar con "*" los campos obligatorios
        for name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} *"