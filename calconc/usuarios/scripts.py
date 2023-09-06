from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .forms import FornecedorForms, TipoAgregadoForms, AgregadoForms, TracoForms, TracoAgregadoForms
from .models import Fornecedor, TipoAgregado, Agregado, Historico, Traco, Usuarios, TracoAgregado
from django.utils import timezone
from django.db.models import F
from datetime import datetime
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib import messages

def GetInformacoesAgregados(agregados_traco, tipos_agregado):
    porcentagem_agregados = []
    for tipo_agregado in tipos_agregado:
        for agregado_traco in agregados_traco:
            if agregado_traco.agregado.fk_tipo_agregado_id == tipo_agregado:
                value = agregado_traco.porcentagem
                break
            else:
                value = ''
        porcentagem_agregados.append(value)

    informacoes_agregados = []
    for index, tipo_agregado in enumerate(tipos_agregado):

        agregados_info = []
        for agregado in tipo_agregado.agregados_relacionados():
            selected = ''
            for agregado_traco in agregados_traco:
                if agregado.id == agregado_traco.agregado_id:
                    selected = 'selected'
            print(agregados_traco)
            agregados_info.append({
                'nome': agregado.nome,
                'id': agregado.id,
                'selected': selected
            })
        info = {
            'tipo_agregado': tipo_agregado.nome,
            'tipo_agregado_id': tipo_agregado.id,
            'porcentagem': str(porcentagem_agregados[index]),
            'agregados': agregados_info
        }
        informacoes_agregados.append(info)

    return informacoes_agregados


def InsertTraco(form, agregados, porcentagem_agregados):
    porcentagem_total = form.cleaned_data['porcentagem_agua']
    for index, agregado_id in enumerate(agregados):
        if agregado_id != '' and porcentagem_agregados[index] != '':
            porcentagem_total = porcentagem_total + float(porcentagem_agregados[index])

    if porcentagem_total != 100:
        # TODO dar erro
        return 'ERROR'

    traco = form.save()

    TracoAgregado.objects.filter(traco=traco).delete()
    # Processar e salvar as porcentagens dos agregados
    for index, agregado_id in enumerate(agregados):
        if agregado_id != '':
            agregado = Agregado.objects.get(id=agregado_id)

            TracoAgregado.objects.create(traco=traco, agregado=agregado,
                                         porcentagem=porcentagem_agregados[index])
    return redirect('traco')
