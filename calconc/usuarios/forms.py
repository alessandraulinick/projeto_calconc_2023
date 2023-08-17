from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUsuario
from django import forms
from .models import Fornecedor
from .models import TipoAgregado, Agregado

class CustomUsuarioCreateForm(UserCreationForm):
    class Meta:
        model = CustomUsuario
        fields = ('first_name', 'last_name', 'fone')
        labels = {'username': 'Username/E-mail'}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["username"]
        if commit:
            user.save()
        return user

class CustomUsuarioChangeForm(UserChangeForm):
    class Meta:
        model = CustomUsuario
        fields = ('first_name', 'last_name', 'fone')

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'cidade', 'id', 'bairro', 'logradouro', 'CEP', 'complemento', 'cpf_cnpj', 'fone_1', 'ie', 'observacao']

class TipoAgregadoForms(forms.ModelForm):
    class Meta:
        model = TipoAgregado
        fields = ['nome']


class AgregadoForms(forms.ModelForm):
    tipo_agregado = forms.ModelChoiceField(queryset=TipoAgregado.objects.all(), label="Tipo de Agregado")

    class Meta:
        model = Agregado
        fields = ['tipo_agregado', 'nome', 'pen_6_30_mm', 'pen_4_80_mm', 'pen_2_40_mm', 'pen_1_20_mm', 'pen_600_um', 'pen_300_um', 'pen_150_um', 'pen_75_um', 'fundo', 'umidade', 'massa_especifica']
