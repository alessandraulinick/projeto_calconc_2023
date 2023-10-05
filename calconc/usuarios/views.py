from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .forms import FornecedorForms, TipoAgregadoForms, AgregadoForms, TracoForms, TracoAgregadoForms, \
    CustomUsuarioCreateForm
from .models import Fornecedor, TipoAgregado, Agregado, Traco, TracoAgregado, CalculoTraco, CustomUsuario, \
    AgregadosCalculo
from django.utils import timezone
from django.db.models import F
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.contrib import messages
from .scripts import GetInformacoesAgregados, InsertTraco, CalcularTraco, get_last_agregado, resolve_unidade_medida
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from django import forms
from textwrap import wrap
from django.core.paginator import Paginator

itens_por_pagina = 5
@login_required
def listar_historico(request):
    historico = CalculoTraco.objects.all()

    exibir_data = True
    return render(request, 'historico/index.html', {'historico': historico, 'exibir_data': exibir_data})


@login_required
def inspecionar_historico(request, calculo_id):
    historico = CalculoTraco.objects.all()

    calculo_traco = CalculoTraco.objects.get(id=calculo_id)
    agregados_calculo = AgregadosCalculo.objects.filter(fk_calculo_traco=calculo_traco)

    return render(request, 'historico/inspecionar.html', {
        'historico': historico,
        'calculo_traco': calculo_traco,
        'agregados_calculo': agregados_calculo
    })



# Calculadora
@login_required
def calculadora(request):
    tracos = Traco.objects.all()
    if request.method == 'POST':
        traco_id = request.POST.get('traco_id')
        volume_traco = float(request.POST.get('volume_traco'))
        unidade_medida = request.POST.get('unidade_medida')

        traco = Traco.objects.get(id=traco_id)

        multiplicador, unidade_medida_display = resolve_unidade_medida(unidade_medida)

        calculo_object = CalcularTraco(volume_traco, traco, multiplicador, unidade_medida_display)

        # Armazena os valores calculados na sessão
        request.session['traco'] = traco.nome
        request.session['volume_traco'] = volume_traco
        request.session['unidade_medida'] = unidade_medida
        request.session['peso_final'] = calculo_object['peso_final']

        calculo_traco = CalculoTraco(
            volume=volume_traco,
            unidade_medida=unidade_medida,
            peso_final=calculo_object['peso_final'],
            fk_usuario=CustomUsuario.objects.get(id=request.user.id),
            fk_traco=traco
        )
        calculo_traco.save()

        for agregado in calculo_object['agregados']:
            agregados_calculo = AgregadosCalculo(
                nome=agregado['nome'],
                tipo_agregado=agregado['tipo_agregado'],
                quantidade=agregado['quantidade'],
                unidade_medida=agregado['unidade_medida'],
                fk_calculo_traco=calculo_traco
            )
            agregados_calculo.save()

        return render(request, 'calculadora/index.html', {'tracos': tracos, 'calculo_object': calculo_object, 'calculo_traco_id': calculo_traco.id})
    else:
        return render(request, 'calculadora/index.html', {'tracos': tracos})


# Tipo Agregado
@login_required
def listar_tipo_agregado(request):
    tipos_agregados = TipoAgregado.objects.all()
    paginator = Paginator(tipos_agregados, 5)

    page_number = request.GET.get("page")
    context = {
        'tipos_agregados': tipos_agregados,
        'page_obj': paginator.get_page(page_number),
        'exibir_data': False
    }
    return render(request, 'tipo_agregado/index.html', context)


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
    exibir_data = False
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
    def get_success_url(self):
        """ Redirects to the newly created object """
        new = self.object
        url = reverse_lazy("my-item", kwargs={"pk": new.pk})
        return url
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
    agregados_traco = TracoAgregado.objects.filter(traco=traco)
    tipos_agregado = TipoAgregado.objects.all()

    context = {
        'traco': traco,
        'informacoes_agregados': GetInformacoesAgregados(agregados_traco, tipos_agregado)
    }
    return render(request, 'traco/inspecionar.html', context)


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
        exibir_data = True
        context = {
            'traco': tracos_filtrados, 'exibir_data': exibir_data
        }

        return render(request, 'traco/index.html', context)


@login_required
def filtrar_historico(request):
    if request.method == 'GET':
        filtro_data = request.GET.get('data')
        filtro_nome = request.GET.get('nome')

        historico_filtrado = CalculoTraco.objects.all()

        if filtro_data:
            data_selecionada = timezone.make_aware(datetime.strptime(filtro_data, '%Y-%m-%d'))
            data_selecionada_date = data_selecionada.date()
            historico_filtrado = historico_filtrado.filter(data_hora__date=data_selecionada_date)
        if filtro_nome:
            historico_filtrado = historico_filtrado.filter(fk_traco__nome__icontains=filtro_nome)
        if 'limpar' in request.GET:
            return HttpResponseRedirect(request.path_info)

        exibir_data = True
        context = {
            'historico': historico_filtrado, 'exibir_data': exibir_data
        }

        return render(request, 'historico/index.html', context)

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


def decrease_y(y):
    y[0] -= 20
    return y[0]

@login_required
def download_pdf(request, calculo_traco_id):

    calculo_traco = CalculoTraco.objects.get(id=calculo_traco_id)
    agregados_calculo = AgregadosCalculo.objects.filter(fk_calculo_traco=calculo_traco)

    _, unidade_medida_display = resolve_unidade_medida(calculo_traco.unidade_medida)

    data_hora = calculo_traco.data_hora
    data_hora_formatado = f"{data_hora.hour}:{data_hora.minute} - {data_hora.day}/{data_hora.month}/{data_hora.year}"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="documento.pdf"'

    p = canvas.Canvas(response)

    # Cordenadas iniciais
    x = [50]
    y = [800]

    # Nome do arquivo
    p.setTitle(calculo_traco.fk_traco.nome)

    p.drawString(x[0], decrease_y(y), f"Traço: {calculo_traco.fk_traco.nome}")

    # Print de Descrição - Isso precisa ser feito pois pode haver quebra de linha aqui
    t = p.beginText()
    t.setTextOrigin(x[0], decrease_y(y))
    wraped_text = wrap(f"Descrição do traço: {calculo_traco.fk_traco.descricao}", 100)
    t.textLines("\n".join(wraped_text))
    p.drawText(t)
    for _ in range(len(wraped_text) - 1):
        decrease_y(y)
    ###

    p.drawString(x[0], decrease_y(y), f"Volume do Traço: {calculo_traco.volume} {unidade_medida_display}")
    p.drawString(x[0], decrease_y(y), f"Peso Final: {calculo_traco.peso_final} Kg")

    p.drawString(x[0], decrease_y(y), f"Data e hora: {data_hora_formatado}")
    p.drawString(x[0], decrease_y(y), f"Usuário: {calculo_traco.fk_usuario.nome}")

    decrease_y(y)
    # Agregados
    p.drawString(x[0], decrease_y(y), f"Agregados")

    column_start = [80, 210, 400]
    p.drawString(column_start[0], decrease_y(y), 'Tipo de Agregado')
    p.drawString(column_start[1], y[0], 'Agregado')
    p.drawString(column_start[2], y[0], 'Quantidade')

    for agregado in agregados_calculo:
        x = [80]
        p.drawString(column_start[0], decrease_y(y), f"{agregado.tipo_agregado}")
        p.drawString(column_start[1], y[0], f"{agregado.nome}")
        p.drawString(column_start[2], y[0], f"{agregado.quantidade} {agregado.unidade_medida}")

    p.showPage()
    p.save()

    return response


@login_required
def listar_usuarios(request):
    usuarios = CustomUsuario.objects.all()
    return render(request, 'registration/index_usuario.html', {'usuarios': usuarios})


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


def inspecionar_usuario(request, pk):
    return render(request, 'registration/inspecionar_usuario.html', null)


def editar_usuario(request, pk):
    return render(request, 'registration/editar_usuario.html', null)


def desativar_usuario(request, pk):
    return null

