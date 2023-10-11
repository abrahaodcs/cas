#usuarios/forms.py

from django import forms
from .models import CustomUser

class EditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['cpf', 'email', 'cargo', 'nivel_acesso', 'nivel_organizacional', 'nome', 'data_nascimento', 'data_ingresso', 'celular']



