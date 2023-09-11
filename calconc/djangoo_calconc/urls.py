from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from usuarios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('django.contrib.auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    #### Calculadora
    path('calculadora/', views.calculadora, name='calculadora'),
    path('download-pdf/<int:calculo_traco_id>/', views.download_pdf, name='download_pdf'),

    #### tipo agregado
    path('tipo_agregado/', views.listar_tipo_agregado, name='tipo_agregado'),
    path('cadastrar_tipo_agregado/', views.cadastrar_tipo_agregado, name='cadastrar_tipo_agregado'),
    path('editar_tipo_agregado/<int:pk>/', views.editar_tipo_agregado, name='editar_tipo_agregado'),
    path('filtrar_tipo_agregados/', views.filtrar_tipo_agregados, name='filtrar_tipo_agregados'),

    ### Historico
    path('historico/', views.listar_historico, name='historico'),
    path('inspectionar_historico/<int:calculo_id>/', views.inspectionar_historico, name='inspectionar_historico'),

    ### Traço
    path('filtrar_tracos/', views.filtrar_tracos, name='filtrar_tracos'),
    path('traco/', views.listar_traco, name='traco'),
    path('cadastrar_traco/', views.cadastrar_traco, name='cadastrar_traco'),
    path('inspecionar_traco/<int:pk>/', views.inspecionar_traco, name='inspecionar_traco'),
    path('deletar_traco/<int:pk>/', views.deletar_traco, name='deletar_traco'),
    path('editar_traco/<int:pk>/', views.editar_traco, name='editar_traco'),

    ### Usuarios
    path('usuarios/', views.listar_usuarios, name='usuarios'),
    path('cadastrar_usuario', views.cadastrar_usuarios, name='cadastrar_usuario'),

    ### Agregados
    path('agregados/', views.listar_agregados, name='agregados'),
    path('cadastrar_agregado/', views.cadastrar_agregado, name='cadastrar_agregado'),
    path('inspecionar_agregado/<int:pk>/', views.inspecionar_agregado, name='inspecionar_agregado'),
    path('editar_agregado/<int:pk>/', views.editar_agregado, name='editar_agregado'),
    path('deletar_agregado/<int:pk>/', views.deletar_agregado, name='deletar_agregado'),
    path('filtrar_agregados/', views.filtrar_agregados, name='filtrar_agregados'),

    ### Fornecedor
    path('fornecedor/', views.listar_fornecedor, name='fornecedor'),
    path('inspecionar_fornecedor/<int:pk>/', views.inspecionar_fornecedor, name='inspecionar_fornecedor'),
    path('cadastrar_fornecedor/', views.cadastrar_fornecedor, name='cadastrar_fornecedor'),
    path('editar_fornecedor/<int:pk>', views.editar_fornecedor, name='editar_fornecedor'),
    path('filtrar_fornecedores/', views.filtrar_fornecedor, name='filtrar_fornecedores'),
]
