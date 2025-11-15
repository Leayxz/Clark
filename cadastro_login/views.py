from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def login_user(request):

      if request.method == "GET":
            return render(request, "login.html")

      if request.method == "POST":
            email = request.POST.get("email")
            senha = request.POST.get("senha")

            # VERIFICA EMAIL E SENHA
            usuario = authenticate(request, username = email, password = senha)
            if usuario == None: return render(request, "login.html", {"erro": "Email ou Senha Inválidos."})

            login(request, usuario)
            print(f"✅ Usuário Autenticado e Logado: {email}")
            return redirect("/aplicacao/pagina_inicial")

      return redirect("/login_user/")

def cadastro_user(request):

      if request.method == "GET":
            return render(request, "cadastro.html")
      
      if request.method == "POST":
            email = request.POST.get('email')
            senha = request.POST.get('senha')

            # VERIFICA SE E VAZIO OU DUPLICADO
            if email == None or senha == None: return render(request, "cadastro.html", {"erro": "Username, Email e Senha São Obrigatórios."})
            if User.objects.filter(username = email).exists(): return render(request, "cadastro.html", {"erro": "Email Já Cadastrado."})

            User.objects.create_user(username = email, password = senha)
            print(f"🔑 Novo Usuário Cadastrado: {email}")
            return redirect("login_user")

      return redirect("/cadastro_user/")

@login_required
def logout_user(request):
      logout(request)
      return redirect('login_user')
