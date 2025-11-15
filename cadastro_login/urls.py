from django.urls import path
from . import views

urlpatterns = [
      path("", views.login_user, name = "login_user"),
      path("cadastro_user/", views.cadastro_user, name = "cadastro_user"),
      path("logout/", views.logout_user, name = "logout"),
]
