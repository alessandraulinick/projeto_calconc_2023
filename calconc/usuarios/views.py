from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .forms import FornecedorForms, TipoAgregadoForms, AgregadoForms, TracoForms
from .models import Fornecedor, TipoAgregado, Agregado, Historico, Traco, Usuarios, TracoAgregado
from django.utils import timezone
from django.db.models import F
from datetime import datetime
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib import messages


@method_decorator(login_required, name='dispatch')
class CalculatorView(TemplateView):
    template_name = 'calculator.html'

    def post(self, request, *args, **kwargs):
        num1 = float(request.POST['num1'])
        num2 = float(request.POST['num2'])
        result = num1 + num2
        return self.render_to_response(self.get_context_data(result=result))


@login_required
def listar_historico(request):  # Renomeei a função para ser mais descritiva
    historico = Historico.objects.all()
    return render(request, 'historico.html', {'historico': historico})


@login_required
def listar_usuarios(request):  # Renomeei a função para ser mais descritiva
    usuarios = Usuarios.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})


############# Tipo Agregado
@login_required
def listar_tipo_agregado(request):
    tipos_agregados = TipoAgregado.objects.all()  # Renomeei a variável para ficar mais claro
    return render(request, 'tipo_agregado/index.html', {'tipos_agregados': tipos_agregados})


@login_required
def cadastrar_tipo_agregado(request):
    if request.method == 'POST':
        form = TipoAgregadoForms(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tipo_agregado')
    else:
        form = TipoAgregadoForms()
    return render(request, 'tipo_agregado/cadastrar.html', {'form': form})


def editar_tipo_agregado(request, pk):
    tipo_agregado = get_object_or_404(TipoAgregado, id=pk)

    if request.method == 'POST':
        form = TipoAgregadoForms(request.POST, instance=tipo_agregado)
        if form.is_valid():
            form.save()
            return redirect('tipo_agregado')  # Redireciona para a página de listagem de agregados
    else:
        form = TipoAgregadoForms(instance=tipo_agregado)

    context = {
        'form': form,
        'tipo_agregado': tipo_agregado
    }
    return render(request, 'tipo_agregado/editar.html', context)


def deletar_tipo_agregado(request, pk):
    tipo_agregado = get_object_or_404(TipoAgregado, pk=pk)
    if request.method == 'POST':
        tipo_agregado.delete()
    return redirect('tipo_agregado')


########## Agregado
@login_required
def listar_agregados(request):  # Renomeei a função para ser mais descritiva
    agregados = Agregado.objects.all()
    return render(request, 'agregado/index.html', {'agregados': agregados})


@login_required
def cadastrar_agregado(request):
    if request.method == 'POST':
        form = AgregadoForms(request.POST)
        if form.is_valid():
            agregado = form.save(commit=False)
            agregado.fk_usuario_id = request.user.id
            print(request.user.id)
            agregado.save()

            Agregado.objects.filter(pk=agregado.pk).update(num_modificacao=F('num_modificacao') + 1)

            return redirect('agregados')
    else:
        form = AgregadoForms()

    tipo_agregado_id = int(request.GET.get('fk_tipo_agregado_id', 0))
    fornecedor_id = int(request.GET.get('fk_fornecedor_id', 0))

    form.fields['fk_tipo_agregado_id'].queryset = TipoAgregado.objects.all()
    form.fields['fk_fornecedor_id'].queryset = Fornecedor.objects.all()

    if tipo_agregado_id:
        form.fields['fk_tipo_agregado_id'].initial = tipo_agregado_id

    if fornecedor_id:
        form.fields['fk_fornecedor_id'].initial = fornecedor_id

    return render(request, 'agregado/cadastrar.html', {'form': form})


@login_required
def inspecionar_agregado(request, pk):
    agregado = get_object_or_404(Agregado, pk=pk)
    return render(request, 'agregado/inspecionar.html', {'agregado': agregado})


def editar_agregado(request, pk):
    agregado = get_object_or_404(Agregado, id=pk)

    if request.method == 'POST':
        form = AgregadoForms(request.POST, instance=agregado)

        # TODO adicnioar logica com numero de modificação Agregado.objects.filter(pk=agregado.pk).update(num_modificacao=F('num_modificacao') + 1)
        if form.is_valid():
            form.save()
            return redirect('agregados')  # Redireciona para a página de listagem de agregados
    else:
        form = AgregadoForms(instance=agregado)

    context = {
        'form': form,
        'agregado': agregado,
    }
    return render(request, 'agregado/editar.html', context)


def deletar_agregado(request, pk):
    agregado = get_object_or_404(Agregado, pk=pk)
    if request.method == 'POST':
        agregado.delete()
    return redirect('agregados')


@login_required
def listar_agregado(request):
    agregados = Agregado.objects.all()
    return render(request, 'agregados', {'agregados': agregados})
############

# Fornecedor
@login_required
def listar_fornecedor(request):
    fornecedores = Fornecedor.objects.all()
    return render(request, 'fornecedor/index.html', {'fornecedores': fornecedores})


@login_required
def inspecionar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    return render(request, 'fornecedor/inspecionar.html', {'fornecedor': fornecedor})


@login_required
def cadastrar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForms(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fornecedor')
        else:
            print("Erro cadastrar_fornecedor")

    else:
        form = FornecedorForms()
    return render(request, 'fornecedor/cadastrar.html', {'form': form})


def editar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, id=pk)

    if request.method == 'POST':
        form = FornecedorForms(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            return redirect('fornecedor')  # Redireciona para a página de fornecedor
    else:
        form = FornecedorForms(instance=fornecedor)

    context = {
        'form': form,
        'fornecedor': fornecedor
    }
    return render(request, 'fornecedor/editar.html', context)
#############

# Traço
@login_required
def listar_traco(request):  # Renomeei a função para ser mais descritiva
    traco = Traco.objects.all()
    return render(request, 'traco/index.html', {'traco': traco})


def cadastrar_traco(request):
    tipos_agregado = TipoAgregado.objects.all()

    if request.method == 'POST':
        form = TracoForms(request.POST)
        print(form.errors)
        if form.is_valid():

            # Processar e salvar as porcentagens dos agregados
            for tipo_agregado in tipos_agregado:
                for agregado in tipo_agregado.agregados.all():
                    porcentagem_key = f'agregado_{tipo_agregado.id}_{agregado.id}'
                    porcentagem = float(request.POST.get(porcentagem_key, 0))

                    if porcentagem > 0:
                        traco_agregado = TracoAgregado(traco=traco, agregado=agregado, porcentagem=porcentagem)
                        traco_agregado.save()

            traco = form.save()
            return redirect('traco')  # Redirecionar para a página de sucesso após o cadastro
    else:
        form = TracoForms()
    return render(request, 'traco/cadastrar.html', {'form': form, 'tipos_agregado': tipos_agregado})

# @login_required
# def cadastrar_traco(request):
#     if request.method == 'POST':
#         traco_form = TracoForms(request.POST)
#         if traco_form.is_valid():
#             traco_form.save()
#             return redirect('traco')
#     else:
#         traco_form = TracoForms()
#
#         tipos_agregados = TipoAgregado.objects.all()
#         agregados = Agregado.objects.all()
#
#         return render(request,
#                       'traco/cadastrar.html',
#                       {
#                           'traco_form': traco_form,
#                           'tipos_agregados': tipos_agregados,
#                           'agregados': agregados,
#                       })


def deletar_traco(request, pk):
    traco = get_object_or_404(Traco, pk=pk)
    if request.method == 'POST':
        traco.delete()
    return redirect('traco')


def editar_traco(request, pk):
    traco = get_object_or_404(Traco, id=pk)

    if request.method == 'POST':
        form = TracoForms(request.POST, instance=traco)
        if form.is_valid():
            form.save()
            return redirect('traco')  # Redireciona para a página de fornecedor
    else:
        form = TracoForms(instance=traco)

    context = {
        'form': form,
        'traco': traco
    }
    return render(request, 'traco/editar.html', context)


def filtrar_tracos(request):
    if request.method == 'GET':
        filtro_data = request.GET.get('data')
        filtro_nome = request.GET.get('nome')

        tracos_filtrados = Traco.objects.all()

        if filtro_data:
            data_selecionada = timezone.make_aware(datetime.strptime(filtro_data, '%Y-%m-%d'))
            data_selecionada_date = data_selecionada.date()
            tracos_filtrados = tracos_filtrados.filter(data_cadastro__date=data_selecionada_date)

        if filtro_nome:
            tracos_filtrados = tracos_filtrados.filter(nome__icontains=filtro_nome)

        if 'limpar' in request.GET:
            return HttpResponseRedirect(request.path_info)

        context = {
            'traco': tracos_filtrados,
        }

        return render(request, 'traco/index.html', context)
