from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from usuarios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('calculator', views.CalculatorView, name='calculator'),
    path('listar_fornecedores/', views.listar_fornecedores, name='listar_fornecedores'),
    path('agregados/', views.listar_agregados, name='agregados'),
    path('tipo_agregado/', views.listar_tipo_agregado, name='tipo_agregado'),
    path('historico/', views.listar_historico, name='historico'),
    path('traco/', views.listar_traco, name='traco'),
    path('usuarios/', views.listar_usuarios, name='usuarios'),
    path('cadastrar_agregado/', views.cadastrar_agregado, name='cadastrar_agregado'),
    path('cadastrar_fornecedor/', views.cadastrar_fornecedor, name='cadastrar_fornecedor'),
    path('cadastrar_tipo_agregado/', views.cadastrar_tipo_agregado, name='cadastrar_tipo_agregado'),
    path('visualizar_agregado/<int:pk>/', views.visualizar_agregado, name='visualizar_agregado'),
    path('editar_agregado/<int:pk>/', views.editar_agregado, name='editar_agregado'),
    path('deletar_agregado/<int:pk>/', views.deletar_agregado, name='deletar_agregado'),
]
