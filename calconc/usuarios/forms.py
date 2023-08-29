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


class FornecedorForms(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'cidade', 'id', 'bairro', 'logradouro', 'CEP', 'complemento', 'cpf_cnpj', 'fone_1', 'ie', 'observacao']


class TipoAgregadoForms(forms.ModelForm):
    class Meta:
        model = TipoAgregado
        fields = ['nome']


class AgregadoForms(forms.ModelForm):
    class Meta:
        model = Agregado
        fields = ['fk_tipo_agregado_id', 'nome', 'pen_6_30_mm', 'pen_4_80_mm', 'pen_2_40_mm', 'pen_1_20_mm', 'pen_600_um', 'pen_300_um', 'pen_150_um', 'pen_75_um', 'fundo', 'umidade', 'massa_especifica', 'fk_fornecedor_id']

    def clean_pen_6_30_mm(self):
        pen_6_30_mm = self.cleaned_data.get('pen_6_30_mm')
        if pen_6_30_mm <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return pen_6_30_mm

    def clean_pen_4_80_mm(self):
        pen_4_80_mm = self.cleaned_data.get('pen_4_80_mm')
        if pen_4_80_mm <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return pen_4_80_mm

    def clean_pen_2_40_mm(self):
        pen_2_40_mm = self.cleaned_data.get('pen_2_40_mm')
        if pen_2_40_mm <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return pen_2_40_mm

    def clean_pen_1_20_mm(self):
        pen_1_20_mm = self.cleaned_data.get('pen_1_20_mm')
        if pen_1_20_mm <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return pen_1_20_mm

    def clean_pen_600_um(self):
        pen_600_um = self.cleaned_data.get('pen_600_um')
        if pen_600_um <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return pen_600_um

    def clean_pen_300_um(self):
        pen_300_um = self.cleaned_data.get('pen_300_um')
        if pen_300_um <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return pen_300_um

    def clean_pen_150_um(self):
        pen_150_um = self.cleaned_data.get('pen_150_um')
        if pen_150_um <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return pen_150_um

    def clean_pen_75_um(self):
        pen_75_um = self.cleaned_data.get('pen_75_um')
        if pen_75_um <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return pen_75_um

    def clean_fundo(self):
        fundo = self.cleaned_data.get('fundo')
        if fundo <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return fundo

    def clean_umidade(self):
        umidade = self.cleaned_data.get('umidade')
        if umidade <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return umidade

    def clean_massa_especifica(self):
        massa_especifica = self.cleaned_data.get('massa_especifica')
        if massa_especifica <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return massa_especifica

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fk_tipo_agregado_id'].queryset = TipoAgregado.objects.all()
        self.fields['fk_fornecedor_id'].queryset = Fornecedor.objects.all()
