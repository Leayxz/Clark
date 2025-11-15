import datetime
from django.http import JsonResponse
from aplicacao.task import rodar_automacao
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .pagamentos import validar_pagamento, gerar_invoice

@login_required()
def pagina_inicial(request):

      user = request.user

      if request.method == 'GET':

            # VERIFICA PAGAMENTO
            pagamento_confirmado = validar_pagamento(user.username)

            # BUSCA DATA EXPIRACAO PARA O HTML
            data_expiracao = None
            if pagamento_confirmado:
                  invoice = cache.get(f"INVOICE_{user.username}")
                  data_expiracao_timestamp = (invoice['timestamp'] / 1000) + 30 * 24 * 60 * 60
                  data_expiracao = datetime.datetime.fromtimestamp(data_expiracao_timestamp)
       
            # TELEGRAM SALVO PARA O HTML
            telegram = cache.get(f"USER_TELEGRAM_{request.user.username}")

            # BUSCA CONFIGS E SETA SE NAO HOUVER
            config = cache.get(f"CONFIGS_USER_{user.username}")
            if config == None:
                  config = { "id_task": False, "quantity1": 0, "quantity2": 0, "quantity3": 0, "quantity4": 0, "preco_referencia": 0, 'comprar_abaixo': 0, "limite_margem": 0, "percentual_lucro": 0.0, "variacao_compra": 0, "percentual_seguranca_liquidacao": 0.0 }
                  cache.set(f"CONFIGS_USER_{user.username}", config, timeout = 30*24*60*60)

            # PAGAMENTO, TASK, PRECO ATUAL E TELEGRAM PRA PAGINA INICIAL
            preco_atual = cache.get('preco_atual')
            return render(request, "pagina_inicial.html", { 'preco_atual': preco_atual, 'id_task': config['id_task'], 'pagamento_confirmado': pagamento_confirmado, 'data_expiracao': data_expiracao, 'telegram': telegram })

      if request.method == 'POST':
            qr_code = gerar_invoice(user.username)
            if qr_code: return JsonResponse(qr_code)
            return JsonResponse({'erro': "Erro Ao Gerar Invoice"})

      return redirect("/aplicacao/pagina_inicial/")

@login_required
def config_automacao(request):

      user = request.user
      config = cache.get(f"CONFIGS_USER_{user.username}")

      if request.method == "GET":

            # PROTECAO ROTA PARA USUARIOS SEM PAGAMENTO
            pagamento_confirmado = validar_pagamento(user.username)
            if pagamento_confirmado:
                  return render(request, "config_automacao.html", {"config": config, 'id_task': config['id_task']})

            return redirect("/aplicacao/pagina_inicial/")

      if request.method == "POST":

            # SALVA AS CONFIGURAÇOES EM CACHE OU REDIRECIONA CASO O USER DIGITE ERRADO
            try:
                  config['quantity1'] = int(request.POST.get("quantity1"))
                  config['quantity2'] = int(request.POST.get("quantity2"))
                  config['quantity3'] = int(request.POST.get("quantity3"))
                  config['quantity4'] = int(request.POST.get("quantity4"))

                  config['preco_referencia'] = float(request.POST.get("preco_referencia"))
                  config['comprar_abaixo'] = float(request.POST.get('comprar_abaixo'))

                  config['percentual_lucro'] = float(request.POST.get("percentual_lucro"))
                  config['variacao_compra'] = int(request.POST.get("variacao_compra"))

                  config['limite_margem'] = int(request.POST.get("limite_margem"))
                  config['percentual_seguranca_liquidacao'] = float(request.POST.get("percentual_seguranca_liquidacao"))

                  cache.set(f"CONFIGS_USER_{user.username}", config, timeout = 30*24*60*60)
                  return redirect("/aplicacao/config_automacao/")

            except:
                  return redirect("/aplicacao/config_automacao/")

      return redirect("/aplicacao/pagina_inicial/")

@login_required
def ligar_desligar_automacao(request):

      if request.method == "POST":

            # CONFIG AUTOMACAO E DADOS API    
            user = request.user
            config = cache.get(f"CONFIGS_USER_{user.username}")
            dados_api = {"API_KEY": request.POST.get("API_KEY"), "SECRET_KEY": request.POST.get("SECRET_KEY")}

            # SE EXISTIR TASK > DESLIGAR REMOVENDO API
            if config['id_task']:
                  config['id_task'] = False
                  cache.set(f"CONFIGS_USER_{user.username}", config, timeout = 30 * 24 * 60 * 60)
                  cache.delete(f"{user.username}_CACHE_API:")
                  print(f"✅ TASK ENCERRADA E API APAGADA")

            # SE NAO EXISTIR TASK > LIGAR
            else:
                  config['id_task'] = True
                  cache.set(f"CONFIGS_USER_{user.username}", config, timeout = 30 * 24 * 60 * 60)
                  cache.set(f"{user.username}_CACHE_API:", dados_api, timeout = 30 * 24 * 60 * 60)
                  rodar_automacao.delay(user.username)
                  print(f"✅ TASK SALVA E ENVIADA")

      return redirect("/aplicacao/config_automacao")

@login_required
def salvar_telegram(request):

      if request.method == 'GET':
            return render(request, "telegram.html")

      if request.method == 'POST':

            TOKEN_TELEGRAM = request.POST.get('TOKEN_TELEGRAM')
            ID_TELEGRAM = request.POST.get('ID_TELEGRAM')

            user_telegram = {'TOKEN_TELEGRAM': TOKEN_TELEGRAM, 'ID_TELEGRAM': ID_TELEGRAM }
            cache.set(f"USER_TELEGRAM_{request.user.username}", user_telegram, timeout = 30 * 24 * 60 * 60)

            return redirect('pagina_inicial')

      return redirect("pagina_inicial")
