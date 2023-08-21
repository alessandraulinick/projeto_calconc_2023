from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .forms import FornecedorForm, TipoAgregadoForms, AgregadoForms
from .models import Fornecedor, TipoAgregado, Agregado, Historico, Traco, Usuarios
from django.utils import timezone
from django.db.models import F


@login_required
class CalculatorView(TemplateView):
    template_name = 'calculator.html'

    def post(self, request, *args, **kwargs):
        num1 = float(request.POST['num1'])
        num2 = float(request.POST['num2'])
        result = num1 + num2
        return self.render_to_response(self.get_context_data(result=result))

@login_required
def listar_fornecedores(request):
    fornecedores = Fornecedor.objects.all()
    return render(request, 'listar_fornecedores.html', {'fornecedores': fornecedores})

@login_required
def listar_tipo_agregado(request):
    tipos_agregados = TipoAgregado.objects.all()  # Renomeei a variável para ficar mais claro
    return render(request, 'tipo_agregado.html', {'tipos_agregados': tipos_agregados})

@login_required
def listar_agregados(request):  # Renomeei a função para ser mais descritiva
    agregados = Agregado.objects.all()
    return render(request, 'agregados.html', {'agregados': agregados})

@login_required
def listar_historico(request):  # Renomeei a função para ser mais descritiva
    historico = Historico.objects.all()
    return render(request, 'historico.html', {'historico': historico})

@login_required
def listar_traco(request):  # Renomeei a função para ser mais descritiva
    traco = Traco.objects.all()
    return render(request, 'traco.html', {'traco': traco})

@login_required
def listar_usuarios(request):  # Renomeei a função para ser mais descritiva
    usuarios = Usuarios.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})

## Cadastros
@login_required
def cadastrar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = FornecedorForm()
    return render(request, 'cadastrar_fornecedor.html', {'form': form})

@login_required
def cadastrar_tipo_agregado(request):
    if request.method == 'POST':
        form = TipoAgregadoForms(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TipoAgregadoForms()
    return render(request, 'cadastrar_tipo_agregado.html', {'form': form})

@login_required
def cadastrar_agregado(request):
    if request.method == 'POST':
        form = AgregadoForms(request.POST)
        if form.is_valid():
            agregado = form.save(commit=False)
            agregado.data_cadastro = timezone.now()
            agregado.usuario = request.user
            agregado.save()

            Agregado.objects.filter(pk=agregado.pk).update(num_modificacao=F('num_modificacao') + 1)

            return redirect('index')
    else:
        form = AgregadoForms()

    tipo_agregado_id = int(request.GET.get('fk_tipo_agregado', 0))
    fornecedor_id = int(request.GET.get('fk_fornecedor', 0))

    form.fields['fk_tipo_agregado'].queryset = TipoAgregado.objects.all()
    form.fields['fk_fornecedor'].queryset = Fornecedor.objects.all()

    if tipo_agregado_id:
        form.fields['fk_tipo_agregado'].initial = tipo_agregado_id

    if fornecedor_id:
        form.fields['fk_fornecedor'].initial = fornecedor_id

    return render(request, 'cadastrar_agregado.html', {'form': form})

@login_required
def visualizar_agregado(request, pk):
    agregado = get_object_or_404(Agregado, pk=pk)  # Alterei para Agregado
    return render(request, 'visualizar_agregado.html', {'agregado': agregado})

def editar_agregado(request, pk):
    agregado = get_object_or_404(Agregado, id=pk)

    if request.method == 'POST':
        form = AgregadoForms(request.POST, instance=agregado)
        if form.is_valid():
            form.save()
            return redirect('agregados')  # Redireciona para a página de listagem de agregados
    else:
        form = AgregadoForms(instance=agregado)

    context = {
        'form': form,
        'agregado': agregado,
    }
    return render(request, 'editar_agregado.html', context)

def deletar_agregado(request, pk):
    agregado = get_object_or_404(Agregado, pk=pk)
    if request.method == 'POST':
        agregado.delete()
    return redirect('agregados')

