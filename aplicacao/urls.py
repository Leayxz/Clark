from django.urls import path
from . import views

urlpatterns = [
     path("pagina_inicial/", views.pagina_inicial, name = "pagina_inicial"),
     path("config_automacao/", views.config_automacao, name = "config_automacao"),
     path("ligar_desligar_automacao/", views.ligar_desligar_automacao, name = "ligar_desligar_automacao"),
     path("salvar_telegram/", views.salvar_telegram, name = "salvar_telegram")
]