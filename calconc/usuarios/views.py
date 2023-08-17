from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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
    listar_tipo_agregado = TipoAgregado.objects.all()  # Fetch all records from the table
    return render(request, 'tipo_agregado.html', {'listar_tipo_agregado': listar_tipo_agregado})

@login_required
def agregados(request):
    agregados = Agregado.objects.all()  # Fetch all records from the table
    return render(request, 'agregados.html', {'agregados': agregados})

@login_required
def historico(request):
    historico = Historico.objects.all()
    return render(request, 'historico.html', {'historico': historico})

@login_required
def traco(request):
    traco = Traco.objects.all()
    return render(request, 'traco.html', {'traco': traco})

@login_required
def usuarios(request):
    usuarios = Usuarios.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})

##Cadastros
@login_required
def cadastrar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirecione para a página desejada após o cadastro bem-sucedido
    else:
        form = FornecedorForm()
    return render(request, 'cadastrar_fornecedor.html', {'form': form})

@login_required
def cadastrar_tipo_agregado(request):
    if request.method == 'POST':
        form = TipoAgregadoForms(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Substitua pelo nome da URL a ser redirecionada após o cadastro
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
            agregado.fk_usuario_id = request.user.id
            agregado.save()

            # Atualize o campo num_modificacao usando F()
            Agregado.objects.filter(pk=agregado.pk).update(num_modificacao=F('num_modificacao') + 1)

            return redirect('index')
    else:
        form = AgregadoForms()
    return render(request, 'cadastrar_agregado.html', {'form': form})


