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
    path('calculator/', views.CalculatorView.as_view(), name='calculator'),
    path('tipo_agregado/', views.listar_tipo_agregado, name='tipo_agregado'),
    path('cadastrar_tipo_agregado/', views.cadastrar_tipo_agregado, name='cadastrar_tipo_agregado'),
    path('editar_tipo_agregado/<int:pk>/', views.editar_tipo_agregado, name='editar_tipo_agregado'),
    path('historico/', views.listar_historico, name='historico'),
    path('traco/', views.listar_traco, name='traco'),
    path('cadastrar_traco/', views.cadastrar_traco, name='cadastrar_traco'),
    path('usuarios/', views.listar_usuarios, name='usuarios'),
    path('agregados/', views.listar_agregados, name='agregados'),
    path('cadastrar_agregado/', views.cadastrar_agregado, name='cadastrar_agregado'),
    path('inspecionar_agregado/<int:pk>/', views.inspecionar_agregado, name='inspecionar_agregado'),
    path('editar_agregado/<int:pk>/', views.editar_agregado, name='editar_agregado'),
    path('deletar_agregado/<int:pk>/', views.deletar_agregado, name='deletar_agregado'),
    path('fornecedor/', views.listar_fornecedor, name='fornecedor'),
    path('cadastrar_fornecedor/', views.cadastrar_fornecedor, name='cadastrar_fornecedor'),
    path('editar_fornecedor/<int:pk>', views.editar_fornecedor, name='editar_fornecedor'),
]
