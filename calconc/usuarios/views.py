from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .forms import FornecedorForms, TipoAgregadoForms, AgregadoForms, TracoForms, TracoAgregadoForms
from .models import Fornecedor, TipoAgregado, Agregado, Historico, Traco, Usuarios, TracoAgregado
from django.utils import timezone
from django.db.models import F
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.contrib import messages
from .scripts import GetInformacoesAgregados, InsertTraco
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet



@login_required
def listar_historico(request):  # Renomeei a função para ser mais descritiva
    historico = Historico.objects.all()
    return render(request, 'historico.html', {'historico': historico})


@login_required
def listar_usuarios(request):  # Renomeei a função para ser mais descritiva
    usuarios = Usuarios.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})


# Calculadora
@login_required
def calculadora(request):
    tracos = Traco.objects.all()
    if request.method == 'POST':
        traco_id = request.POST.get('traco_id')
        volume_traco = request.POST.get('volume_traco')
        unidade_medida = request.POST.get('unidade_medida')

        traco = Traco.objects.get(id=traco_id)
        agregados_traco = TracoAgregado.objects.filter(traco=traco)
        if unidade_medida == 'm3':
            multiplicador = 1000
        elif unidade_medida == 'L':
            multiplicador = 1
        else:
            # TODO Erro
            return None


        peso_final = 1*multiplicador*(traco.porcentagem_agua/100)
        agregados_info = [{
            'nome': 'Água',
            'id': '0',
            'quantidade': 1*multiplicador*(traco.porcentagem_agua/100),
            'unidade_medida': 'Litros'
        }]

        for agregado_traco in agregados_traco:
            massa_especifica = agregado_traco.agregado.massa_especifica
            porcentagem = agregado_traco.porcentagem

            peso_final = peso_final + massa_especifica*multiplicador*(porcentagem/100)
            agregados_info.append({
                'nome': agregado_traco.agregado.nome,
                'id': agregado_traco.agregado.id,
                'quantidade': massa_especifica*multiplicador*(porcentagem/100),
                'unidade_medida': 'Kg'
            })

            # Armazene os valores calculados na sessão
            request.session['traco'] = traco.nome
            request.session['volume_traco'] = volume_traco
            request.session['unidade_medida'] = unidade_medida
            request.session['peso_final'] = peso_final

            calculo_object = {
                'traco': {
                    'nome': traco.nome,
                    'id': traco.id
                },
                'volume_traco': volume_traco,
                'unidade_medida': unidade_medida,
                'peso_final': peso_final,
                'agregados': agregados_info
            }

            # TODO salvar em banco, se necessário
        return render(request, 'calculadora/index.html',  {'tracos': tracos, 'calculo_object': calculo_object})
    else:
        return render(request, 'calculadora/index.html',  {'tracos': tracos})
#############

# Tipo Agregado
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
    return render(request, 'traco/index.html', {'traco': traco})


@login_required
def inspecionar_traco(request, pk):
    traco = get_object_or_404(Traco, id=pk)
    return render(request, 'traco/inspecionar.html', {'traco': traco})


@login_required
def cadastrar_traco(request):
    if request.method == 'POST':
        form = TracoForms(request.POST)
        agregados = request.POST.getlist('agregados')
        porcentagem_agregados = request.POST.getlist('porcentagem_agregados')
        print(form.errors)
        if form.is_valid() and (agregados is not None) and (porcentagem_agregados is not None):
            return InsertTraco(form, agregados, porcentagem_agregados)
        else:
            # TODO deu ruim
            return None
    else:
        tipos_agregado = TipoAgregado.objects.all()
        form = TracoForms()

        return render(request, 'traco/cadastrar.html', {'form': form, 'tipos_agregado': tipos_agregado})


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

    if request.method == 'POST':
        form = TracoForms(request.POST, instance=traco)
        agregados = request.POST.getlist('agregados')
        porcentagem_agregados = request.POST.getlist('porcentagem_agregados')

        if form.is_valid() and (agregados is not None) and (porcentagem_agregados is not None):
            return InsertTraco(form, agregados, porcentagem_agregados)
        else:
            # TODO deu ruim
            return None
    else:
        form = TracoForms(instance=traco)
        agregados_traco = TracoAgregado.objects.filter(traco=traco)
        tipos_agregado = TipoAgregado.objects.all()

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

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redireciona para a página inicial após o cadastro
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
