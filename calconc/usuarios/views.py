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
from .scripts import GetInformacoesAgregados, InsertTraco, CalcularTraco, get_last_agregado, resolve_unidade_medida, get_user_group
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from django import forms
from textwrap import wrap
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.shortcuts import render
from .decorators import allowed_users
from django.contrib.auth.models import Group
from .apps import default_calconc_users
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors



itens_por_pagina = 8


def custom_404(request, exception):
    return render(request, 'utils/404.html', status=404)


def custom_500(request):
    return render(request, 'utils/500.html', status=500)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Consultor', 'Editor'])
def index(request):
    context = {
        'user_group': get_user_group(request)
    }
    return render(request, 'index.html', context)

@login_required
@allowed_users(allowed_roles=['Administrador', 'Consultor', 'Editor'])
def listar_historico(request):
    historico = CalculoTraco.objects.all()

    exibir_data = True

    context = {
        'historico': historico,
        'exibir_data': exibir_data,
        'user_group': get_user_group(request)
    }
    return render(request, 'historico/index.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Consultor', 'Editor'])
def inspecionar_historico(request, calculo_id):
    historico = CalculoTraco.objects.all()

    calculo_traco = CalculoTraco.objects.get(id=calculo_id)
    agregados_calculo = AgregadosCalculo.objects.filter(fk_calculo_traco=calculo_traco)

    context = {
        'historico': historico,
        'calculo_traco': calculo_traco,
        'agregados_calculo': agregados_calculo,
        'user_group': get_user_group(request)
    }
    return render(request, 'historico/inspecionar.html', context)


# Calculadora
@login_required
@allowed_users(allowed_roles=['Administrador', 'Consultor', 'Editor'])
def calculadora(request):
    tracos = Traco.objects.all()
    context = {
        'tracos': tracos,
        'user_group': get_user_group(request)
    }
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

        context['calculo_object'] = calculo_object
        context['calculo_traco_id'] = calculo_traco.id

        return render(request, 'calculadora/index.html', context)
    else:
        return render(request, 'calculadora/index.html', context)


# Tipo Agregado
@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def listar_tipo_agregado(request):
    tipos_agregados = TipoAgregado.objects.all().order_by(Lower('nome'))
    exibir_data = False
    paginator = Paginator(tipos_agregados, 6)

    page_number = request.GET.get("page")
    context = {
        'tipos_agregados': tipos_agregados,
        'page_obj': paginator.get_page(page_number),
        'exibir_data': exibir_data,
        'user_group': get_user_group(request)
    }
    return render(request, 'tipo_agregado/index.html', context)

@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def cadastrar_tipo_agregado(request):

    context = {
        'user_group': get_user_group(request)
    }
    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('tipo_agregado')
        form = TipoAgregadoForms(request.POST)

        if form.is_valid():
            form.save()
            return redirect('tipo_agregado')
        else:
            context['form'] = form
            return render(request, 'tipo_agregado/cadastrar.html',context)
    else:
        form = TipoAgregadoForms()
        context['form'] = form

        return render(request, 'tipo_agregado/cadastrar.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def editar_tipo_agregado(request, pk):
    tipo_agregado = get_object_or_404(TipoAgregado, id=pk)

    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('tipo_agregado')
        form = TipoAgregadoForms(request.POST, instance=tipo_agregado)
        if form.is_valid():
            form.save()
            return redirect('tipo_agregado')  # Redireciona para a página de listagem de agregados
    else:
        form = TipoAgregadoForms(instance=tipo_agregado)

    context = {
        'form': form,
        'tipo_agregado': tipo_agregado,
        'user_group': get_user_group(request)
    }
    return render(request, 'tipo_agregado/editar.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def deletar_tipo_agregado(request, pk):
    tipo_agregado = get_object_or_404(TipoAgregado, pk=pk)
    if request.method == 'POST':
        tipo_agregado.delete()
    return redirect('tipo_agregado')


#############


# Agregado
@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def listar_agregados(request):  # Renomeei a função para ser mais descritiva
    agregados = Agregado.objects.all().order_by(Lower('nome'))
    exibir_data = False
    context = {
        'agregados': agregados,
        'exibir_data': exibir_data,
        'user_group': get_user_group(request)
        }
    return render(request, 'agregado/index.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def cadastrar_agregado(request):
    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('agregados')
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

    context = {
        'form': form,
        'user_group': get_user_group(request)
    }

    return render(request, 'agregado/cadastrar.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def inspecionar_agregado(request, pk):
    agregado = get_object_or_404(Agregado, pk=pk)
    context = {
        'agregado': agregado,
        'user_group': get_user_group(request)
    }
    return render(request, 'agregado/inspecionar.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def editar_agregado(request, pk):
    agregado = get_object_or_404(Agregado, id=pk)

    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('agregados')
        form = AgregadoForms(request.POST, instance=agregado)

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
        'user_group': get_user_group(request)
    }
    return render(request, 'agregado/editar.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def deletar_agregado(request, pk):
    agregado = get_object_or_404(Agregado, pk=pk)
    if request.method == 'POST':
        agregado.delete()
    return redirect('agregados')


############

# Fornecedor
@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def listar_fornecedor(request):
    fornecedores = Fornecedor.objects.all().order_by(Lower('nome'))
    exibir_data = False
    context = {
        'fornecedores': fornecedores,
        'exibir_data': exibir_data,
        'user_group': get_user_group(request)
    }
    return render(request, 'fornecedor/index.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def inspecionar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    return render(request, 'fornecedor/inspecionar.html', {'fornecedor': fornecedor})


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def cadastrar_fornecedor(request):
    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('fornecedor')
        form = FornecedorForms(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fornecedor')
        else:
            context = {
                'form': form,
                'user_group': get_user_group(request),
                'errors': {
                    'code': 2,
                    'message': f"O formulário enviado não é válido: {form.errors}"
                }}
        return render(request, 'fornecedor/cadastrar.html', context)

    else:
        form = FornecedorForms()
    context = {
        'form': form,
        'user_group': get_user_group(request)
    }
    return render(request, 'fornecedor/cadastrar.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def editar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, id=pk)

    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('fornecedor')
        form = FornecedorForms(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            return redirect('fornecedor')  # Redireciona para a página de fornecedor
    else:
        form = FornecedorForms(instance=fornecedor)

    context = {
        'form': form,
        'fornecedor': fornecedor,
        'user_group': get_user_group(request)
    }
    return render(request, 'fornecedor/editar.html', context)


#############

# Traço
@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def listar_traco(request):  # Renomeei a função para ser mais descritiva
    traco = Traco.objects.all().order_by(Lower('nome'))
    exibir_data = True
    context = {
        'traco': traco,
        'exibir_data': exibir_data,
        'user_group': get_user_group(request)
    }
    return render(request, 'traco/index.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def inspecionar_traco(request, pk):
    traco = get_object_or_404(Traco, id=pk)
    agregados_traco = TracoAgregado.objects.filter(traco=traco)
    tipos_agregado = TipoAgregado.objects.all()

    context = {
        'traco': traco,
        'informacoes_agregados': GetInformacoesAgregados(agregados_traco, tipos_agregado),
        'user_group': get_user_group(request)
    }
    return render(request, 'traco/inspecionar.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador'])
def cadastrar_traco(request):
    tipos_agregado = TipoAgregado.objects.all()
    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('traco')
        form = TracoForms(request.POST)
        agregados = request.POST.getlist('agregados')
        porcentagem_agregados = request.POST.getlist('porcentagem_agregados')

        context = {
            'form': form,
            'tipos_agregado': tipos_agregado,
            'user_group': get_user_group(request)
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
            'tipos_agregado': tipos_agregado,
            'user_group': get_user_group(request)
        }

        return render(request, 'traco/cadastrar.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def deletar_traco(request, pk):
    traco = get_object_or_404(Traco, pk=pk)
    if request.method == 'POST':
        TracoAgregado.objects.filter(traco=traco).delete()
        traco.delete()
    return redirect('traco')


@login_required
@allowed_users(allowed_roles=['Administrador'])
def editar_traco(request, pk):
    traco = get_object_or_404(Traco, id=pk)
    agregados_traco = TracoAgregado.objects.filter(traco=traco)
    tipos_agregado = TipoAgregado.objects.all()

    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('traco')
        form = TracoForms(request.POST, instance=traco)
        agregados = request.POST.getlist('agregados')
        porcentagem_agregados = request.POST.getlist('porcentagem_agregados')

        context = {
            'form': form,
            'traco': traco,
            'informacoes_agregados': GetInformacoesAgregados(agregados_traco, tipos_agregado),
            'user_group': get_user_group(request)
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
            'informacoes_agregados': GetInformacoesAgregados(agregados_traco, tipos_agregado),
            'user_group': get_user_group(request)
        }

        return render(request, 'traco/editar.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
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
            'traco': tracos_filtrados,
            'exibir_data': exibir_data,
            'user_group': get_user_group(request)
        }

        return render(request, 'traco/index.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
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
            'historico': historico_filtrado,
            'exibir_data': exibir_data,
            'user_group': get_user_group(request)
        }

        return render(request, 'historico/index.html', context)

@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
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
            'agregados': agregados_filtrados,
            'exibir_data': exibir_data,
            'user_group': get_user_group(request)
        }

        return render(request, 'agregado/index.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
def filtrar_tipo_agregados(request):
    if request.method == 'GET':
        filtro_nome = request.GET.get('nome')

        tipo_agregados_filtrados = TipoAgregado .objects.all()

        if filtro_nome:
            tipo_agregados_filtrados = tipo_agregados_filtrados.filter(nome__icontains=filtro_nome)
        if 'limpar' in request.GET:
            return HttpResponseRedirect(request.path_info)
        context = {
            'tipos_agregados': tipo_agregados_filtrados,
            'user_group': get_user_group(request)
        }

        return render(request, 'tipo_agregado/index.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador', 'Editor'])
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
            'user_group': get_user_group(request)
        }

        return render(request, 'fornecedor/index.html', context)


def decrease_y(y):
    y[0] -= 20
    return y[0]

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from django.http import HttpResponse
from datetime import datetime

def create_pdf_with_footer(buffer, content, footer_text):
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=60)
    styles = getSampleStyleSheet()
    story = []

    # Add content to the PDF
    story += content

    # Add a spacer to create space for the footer
    story.append(Spacer(1, 20))

    # Add the footer text
    footer_style = ParagraphStyle(
        name='FooterStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.black,
        alignment=1  # 1 corresponds to TA_CENTER (centered text)
    )

    footer_paragraph = Paragraph(footer_text, footer_style)
    story.append(footer_paragraph)

    doc.build(story)

@login_required
@allowed_users(allowed_roles=['Administrador', 'Consultor', 'Editor'])
def download_pdf(request, calculo_traco_id):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []
    content = []

    # Customize your paragraph styles
    custom_style_center = ParagraphStyle(
        name='CustomStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        alignment=1  # 1 corresponds to TA_CENTER (centered text)
    )

    custom_style = ParagraphStyle(
        name='CustomStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        spaceAfter=12,
        textColor=colors.black
    )

    # Start adding content to the PDF
    calculo_traco = CalculoTraco.objects.get(id=calculo_traco_id)
    traco = CalculoTraco.objects.get(id=calculo_traco_id)
    agregados_calculo = AgregadosCalculo.objects.filter(fk_calculo_traco=traco)
    _, unidade_medida_display = resolve_unidade_medida(calculo_traco.unidade_medida)
    data_hora = calculo_traco.data_hora
    data_hora_formatado = f"{data_hora.hour}:{data_hora.minute} - {data_hora.day}/{data_hora.month}/{data_hora.year}"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio.pdf'

    # Calculate the vertical center position
    vertical_center = (letter[1] - doc.topMargin - doc.bottomMargin) / 2

    # Add a title
    title = "Relatório do Traço"

    story.append(Paragraph(title, styles['Title']))
    story.append(Paragraph("_______________________________________________________________________________", custom_style))

    # Add Traço information
    user_name = f"Usuário: {traco.fk_usuario.first_name} {traco.fk_usuario.last_name}"
    story.append(Paragraph(user_name, custom_style_center))

    # Add Traço information
    story.append(Paragraph(f"Traço: {traco.fk_traco.nome}", custom_style))
    description = "Descrição do traço: " + traco.fk_traco.descricao
    story.append(Spacer(1, 12))
    story.append(Paragraph(description, custom_style))
    story.append(Paragraph(f"Volume do Traço: {traco.volume} {unidade_medida_display}", custom_style))
    story.append(Paragraph(f"Peso Final: {traco.peso_final} Kg", custom_style))

    story.append(Spacer(1, 24))

    # Add Agregados information in a table
    data = [["Tipo de Agregado", "Agregado", "Quantidade"]]
    for agregado in agregados_calculo:
        data.append([agregado.tipo_agregado, agregado.nome, f"{agregado.quantidade} {agregado.unidade_medida}"])

    # Defina uma lista de larguras de coluna desejadas
    column_widths = [100, 200, 200, 500]

    # Crie a tabela com os dados
    table = Table(data, colWidths=column_widths)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Define a cor de fundo da primeira linha como azul
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Define a cor do texto na primeira linha como branco
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold', colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Define a cor de fundo do restante da tabela como cinza
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(table)

    data_hora = datetime.now().strftime("%H:%M - %d/%m/%Y")
    footer_text = f"Data e hora: {data_hora}"

    create_pdf_with_footer(buffer, story, footer_text)

    buffer.seek(0)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio.pdf"'
    response.write(buffer.read())
    return response


@login_required
@allowed_users(allowed_roles=['Administrador'])
@login_required
def listar_usuarios(request):
    usuarios = CustomUsuario.objects.all().order_by(Lower('username'))
    context = {
        'usuarios': usuarios,
        'user_group': get_user_group(request)
    }
    return render(request, 'registration/index_usuario.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador'])
def cadastrar_usuarios(request):
    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('usuarios')
        form = CustomUsuarioCreateForm(request.POST)
        group_name = request.POST.get('group')
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            return redirect('usuarios')

    else:
        form = CustomUsuarioCreateForm()

    context = {
        'form': form,
        'groups': default_calconc_users,
        'user_group': get_user_group(request)
    }
    return render(request, 'registration/cadastrar_usuario.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador'])
def inspecionar_usuario(request, pk):
    # TODO - implementar isso
    return render(request, 'registration/inspecionar_usuario.html', null)


@login_required
@allowed_users(allowed_roles=['Administrador'])
def editar_usuario(request, pk):
    usuario = get_object_or_404(CustomUsuario, id=pk)
    current_group = usuario.groups.all()[0].name

    if request.method == 'POST':
        if "cancel" in request.POST:
            return redirect('usuarios')
        form = CustomUsuarioCreateForm(request.POST, instance=usuario)
        group_name = request.POST.get('group')
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name=group_name)
            # caso o grupo seja editado, removemos o usuário do grupo atual, e adicionamos o novo
            if current_group != group:
                user.groups.remove(Group.objects.get(name=current_group))
                user.groups.add(group)
            return redirect('usuarios')
    else:
        form = CustomUsuarioCreateForm(instance=usuario)

    context = {
        'form': form,
        'usuario': usuario,
        'current_group': current_group,
        'groups': default_calconc_users,
        'user_group': get_user_group(request)
    }
    return render(request, 'registration/editar_usuario.html', context)


@login_required
@allowed_users(allowed_roles=['Administrador'])
def desativar_usuario(request, pk):
    # TODO - testar isso
    usuario = get_object_or_404(CustomUsuario, id=pk)
    form = CustomUsuarioCreateForm(instance=usuario)
    form.inactivate()
    return listar_usuarios(request)

def error_page(request):
    return render(request, 'utils/erro_autorizacao.html')