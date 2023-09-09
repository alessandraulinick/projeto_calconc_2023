from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .forms import FornecedorForms, TipoAgregadoForms, AgregadoForms, TracoForms, TracoAgregadoForms, CustomUsuarioCreateForm
from .models import Fornecedor, TipoAgregado, Agregado, Historico, Traco, Usuarios, TracoAgregado
from django.utils import timezone
from django.db.models import F
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.contrib import messages
from .scripts import GetInformacoesAgregados, InsertTraco, CalcularTraco, get_last_agregado
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from django import forms



@login_required
def listar_historico(request):
    historico = Historico.objects.all()
    return render(request, 'historico.html', {'historico': historico})


@login_required
def listar_usuarios(request):
    usuarios = Usuarios.objects.all()
    return render(request, 'registration/index_usuario.html', {'usuarios': usuarios})


# Calculadora
@login_required
def calculadora(request):
    tracos = Traco.objects.all()
    if request.method == 'POST':
        traco_id = request.POST.get('traco_id')
        volume_traco = float(request.POST.get('volume_traco'))
        unidade_medida = request.POST.get('unidade_medida')

        traco = Traco.objects.get(id=traco_id)

        if unidade_medida == 'm3':
            multiplicador = 1000
            unidade_medida_display = 'Metro(s) cúbico(s) (m³)'
        elif unidade_medida == 'l':
            multiplicador = 1
            unidade_medida_display = 'Litro(s) (l)'
        else:
            # TODO Erro
            return None

        calculo_object = CalcularTraco(volume_traco, traco, multiplicador, unidade_medida_display)

        # Armazena os valores calculados na sessão
        request.session['traco'] = traco.nome
        request.session['volume_traco'] = volume_traco
        request.session['unidade_medida'] = unidade_medida
        request.session['peso_final'] = calculo_object['peso_final']

            # TODO salvar em banco
        return render(request, 'calculadora/index.html',  {'tracos': tracos, 'calculo_object': calculo_object})
    else:
        return render(request, 'calculadora/index.html',  {'tracos': tracos})


# Tipo Agregado
@login_required
def listar_tipo_agregado(request):
    tipos_agregados = TipoAgregado.objects.all()
    exibir_data = True
    return render(request, 'tipo_agregado/index.html', {'tipos_agregados': tipos_agregados, 'exibir_data': exibir_data})


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
#############


# Agregado
@login_required
def listar_agregados(request):  # Renomeei a função para ser mais descritiva
    agregados = Agregado.objects.all()
    exibir_data = True
    return render(request, 'agregado/index.html', {'agregados': agregados, 'exibir_data': exibir_data})


@login_required
def cadastrar_agregado(request):
    if request.method == 'POST':
        form = AgregadoForms(request.POST)
        if form.is_valid():
            agregado = form.save(commit=False)
            agregado.fk_usuario_id = request.user.id
            agregado.save()

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
            agregado = form.save(commit=False)
            agregado.fk_usuario_id = request.user.id
            # get_last_agregado(agregado.id)
            # agregado.num_modificacao = ''
            agregado.save()

            return redirect('agregados')
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

############

# Fornecedor
@login_required
def listar_fornecedor(request):
    fornecedores = Fornecedor.objects.all()
    exibir_data = False
    return render(request, 'fornecedor/index.html', {'fornecedores': fornecedores, 'exibir_data': exibir_data})

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


@login_required
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
    exibir_data = True
    return render(request, 'traco/index.html', {'traco': traco, 'exibir_data': exibir_data})


@login_required
def inspecionar_traco(request, pk):
    traco = get_object_or_404(Traco, id=pk)
    return render(request, 'traco/inspecionar.html', {'traco': traco})


@login_required
def cadastrar_traco(request):
    tipos_agregado = TipoAgregado.objects.all()
    if request.method == 'POST':
        form = TracoForms(request.POST)
        agregados = request.POST.getlist('agregados')
        porcentagem_agregados = request.POST.getlist('porcentagem_agregados')

        context = {
            'form': form,
            'tipos_agregado': tipos_agregado
        }

        if form.is_valid() and (agregados is not None) and (porcentagem_agregados is not None):
            return InsertTraco(request, context, agregados, porcentagem_agregados, render_file='traco/cadastrar.html')
        else:
            context['errors'] = {
                    'code': 2,
                    'message': f"O formulário enviado não é válido: {form.errors}"
                }
            return render(request, 'traco/cadastrar.html', context)
    else:
        form = TracoForms()

        context = {
            'form': form,
            'tipos_agregado': tipos_agregado
        }

        return render(request, 'traco/cadastrar.html', context)


@login_required
def deletar_traco(request, pk):
    traco = get_object_or_404(Traco, pk=pk)
    if request.method == 'POST':
        TracoAgregado.objects.filter(traco=traco).delete()
        traco.delete()
    return redirect('traco')


@login_required
def editar_traco(request, pk):
    traco = get_object_or_404(Traco, id=pk)
    agregados_traco = TracoAgregado.objects.filter(traco=traco)
    tipos_agregado = TipoAgregado.objects.all()

    if request.method == 'POST':
        form = TracoForms(request.POST, instance=traco)
        agregados = request.POST.getlist('agregados')
        porcentagem_agregados = request.POST.getlist('porcentagem_agregados')

        context = {
            'form': form,
            'traco': traco,
            'informacoes_agregados': GetInformacoesAgregados(agregados_traco, tipos_agregado)
        }

        if form.is_valid() and (agregados is not None) and (porcentagem_agregados is not None):
            return InsertTraco(request, context, agregados, porcentagem_agregados, render_file='traco/editar.html')
        else:
            context['errors'] = {
                    'code': 2,
                    'message': f"O formulário enviado não é válido: {form.errors}"
                }
            return render(request, 'traco/editar.html', context)
    else:
        form = TracoForms(instance=traco)

        context = {
            'form': form,
            'traco': traco,
            'informacoes_agregados': GetInformacoesAgregados(agregados_traco, tipos_agregado)
        }

        return render(request, 'traco/editar.html', context)


@login_required
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

@login_required
def filtrar_agregados(request):
    if request.method == 'GET':
        filtro_data = request.GET.get('data')
        filtro_nome = request.GET.get('nome')

        agregados_filtrados = Agregado.objects.all()

        if filtro_data:
            data_selecionada = timezone.make_aware(datetime.strptime(filtro_data, '%Y-%m-%d'))
            data_selecionada_date = data_selecionada.date()
            agregados_filtrados = agregados_filtrados.filter(data_cadastro__date=data_selecionada_date)
        if filtro_nome:
            agregados_filtrados = agregados_filtrados.filter(nome__icontains=filtro_nome)
        if 'limpar' in request.GET:
            return HttpResponseRedirect(request.path_info)

        exibir_data = True
        context = {
            'agregados': agregados_filtrados, 'exibir_data': exibir_data
        }

        return render(request, 'agregado/index.html', context)


@login_required
def filtrar_tipo_agregados(request):
    if request.method == 'GET':
        filtro_data = request.GET.get('data')
        filtro_nome = request.GET.get('nome')

        tipo_agregados_filtrados = TipoAgregado.objects.all()

        if filtro_data:
            data_selecionada = timezone.make_aware(datetime.strptime(filtro_data, '%Y-%m-%d'))
            data_selecionada_date = data_selecionada.date()
            tipo_agregados_filtrados = tipo_agregados_filtrados.filter(data_cadastro__date=data_selecionada_date)
        if filtro_nome:
            tipo_agregados_filtrados = tipo_agregados_filtrados.filter(nome__icontains=filtro_nome)
        if 'limpar' in request.GET:
            return HttpResponseRedirect(request.path_info)
        exibir_data = True
        context = {
            'tipos_agregados': tipo_agregados_filtrados, 'exibir_data': exibir_data
        }

        return render(request, 'tipo_agregado/index.html', context)

@login_required
def filtrar_fornecedor(request):
    if request.method == 'GET':
        filtro_nome = request.GET.get('nome')

        fornecedores_filtrados = Fornecedor.objects.all()

        if filtro_nome:
            fornecedores_filtrados = fornecedores_filtrados.filter(nome__icontains=filtro_nome)
        if 'limpar' in request.GET:
            return HttpResponseRedirect(request.path_info)

        context = {
            'fornecedores': fornecedores_filtrados,
        }

        return render(request, 'fornecedor/index.html', context)


@login_required
def download_pdf(request):
    traco = request.session.get('traco', 'Valor padrão para o traço')
    volume_traco = request.session.get('volume_traco', 'Valor padrão para o volume do traço')
    unidade_medida = request.session.get('unidade_medida', 'Unidade de medida padrão')
    peso_final = request.session.get('peso_final', 0)  # 0 ou outro valor padrão

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="documento.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 730, f"Traço: {traco}")
    p.drawString(100, 710, f"Volume do Traço: {volume_traco} kg")
    p.drawString(100, 690, f"Peso Final: {peso_final}")

    # Adicione os agregados ao PDF
    # Certifique-se de que os valores necessários da sessão estejam disponíveis aqui
    agregados_info = request.session.get('agregados', [])
    y = 670
    for agregado in agregados_info:
        p.drawString(100, y, f"{agregado['nome']}: {agregado['quantidade']} {agregado['unidade_medida']}")
        y -= 20

    p.showPage()
    p.save()

    return response

def cadastrar_usuarios(request):
    if request.method == 'POST':
        form = CustomUsuarioCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('usuarios')  # Redireciona para a página inicial após o cadastro
    else:
        form = CustomUsuarioCreateForm()
    return render(request, 'registration/cadastrar_usuario.html', {'form': form})
