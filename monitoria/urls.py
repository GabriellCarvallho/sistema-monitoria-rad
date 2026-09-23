from django.urls import path

from . import views

app_name = "artigos"

urlpatterns = [
    path("", views.index, name="lista"),
    path('duvidas/nova/', views.DuvidaCreateView.as_view(), name='duvida_create'),
    path('duvidas/<int:pk>/', views.DuvidaDetailView.as_view(), name='duvida_detail'),
    path('duvidas/<int:pk>/assumir/', views.assumir_duvida, name='duvida_assumir'),
    path('duvidas/<int:pk>/responder/', views.ResponderDuvidaView.as_view(), name='duvida_responder'),
    path('duvidas/<int:pk>/encerrar/', views.encerrar_duvida, name='duvida_encerrar'),
    path('base/', views.BaseConhecimentoView.as_view(), name='base_conhecimento'),
    ]