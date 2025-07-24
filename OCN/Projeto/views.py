from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.hashers import check_password 
from django.contrib.auth.hashers import make_password
import json
from django.http import JsonResponse
from datetime import datetime

# Para envio do email
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.cache import cache
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
import random
import string
import uuid

def login_view(request):
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Json inválido'}, status=400)
        
        success, msg, user_id, tipo, nome = login(data)

        if success:
            # Armazenando na sessão
            request.session['usuario_id'] = user_id
            request.session['usuario_tipo'] = tipo
            request.session['usuario_nome'] = nome

        return JsonResponse({
            'success': success,
            'message': msg,
            'redirect_url': '/home' if success else ''
        })

    # Caso seja GET, apenas renderiza o formulário normalmente
    return render(request, 'Projeto/login.html')
          
def login(data):
    email = data.get('email')
    senha = data.get('senha')

    if not data.get("email") or not data.get("senha"):
        return False, "Preencha todos os campos", None, None, None

    try:
        usuario = Usuario.objects.get(email=email)
        if check_password(senha, usuario.senha):
            
            tipo = usuario.tipo  # Cliente ou Barbeiro
            # Buscar o nome do usuário a partir do tipo
            if tipo == 'Cliente':
                nome = Cliente.objects.get(id=usuario.id).nome
            elif tipo == 'Barbeiro':
                nome = Barbeiro.objects.get(id=usuario.id).nome

            return True, "Login realizado com sucesso!", usuario.id, tipo, nome
        
        return False, "Senha incorreta", None, None, None
    except Usuario.DoesNotExist:
        return False, "Usuario não encontrado", None, None, None

def cadastro_view(request):
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'JSON inválido'}, status=400)

        success, msg = cadastro(data)

        return JsonResponse({'success': success, 'message': msg})

    # Caso seja GET, apenas renderiza o formulário normalmente
    return render(request, 'Projeto/cadastro.html')

def cadastro(data):
    nome = data.get('nome')
    senha = data.get('senha')
    tipo = data.get('tipo')
    telefone = data.get('telefone')
    data_nascimento = data.get('data_nascimento')
    email = data.get('email')
    cidade = data.get('cidade')
    cpf = data.get('cpf')

    # Verifica se login já existe
    if Usuario.objects.filter(email=email).exists():
        return False, "Email já cadastrado"
    
    campos = ['nome', 'senha', 'tipo', 'telefone', 'data_nascimento', 'email', 'cidade', 'cpf']
    for campo in campos:
        if not data.get(campo):
            return False, "Preencha todos os campos"

    # Criação do usuário (com senha criptografada)
    usuario = Usuario(
        email=email,
        senha=make_password(senha),
        tipo=tipo
    )
    usuario.save()  # Aqui o ID do usuário é gerado automaticamente

    # Criação de registro específico de acordo com o tipo
    if tipo == 'Cliente':
        # Atribuindo o objeto Usuario ao campo id
        cliente = Cliente(
            id=usuario,  # Aqui estamos passando a instância do Usuario
            cpf=cpf,
            nome=nome,
            telefone=telefone,
            data_nascimento=data_nascimento,
            cidade=cidade
        )
        cliente.save()
    
    elif tipo == 'Barbeiro':
        # Atribuindo o objeto Usuario ao campo id
        barbeiro = Barbeiro(
            id=usuario,  # Aqui estamos passando a instância do Usuario
            cpf=cpf,
            nome=nome,
            telefone=telefone,
            data_nascimento=data_nascimento,
            cidade=cidade
        )
        barbeiro.save()

    # Se o cadastro foi bem-sucedido, exibe a mensagem de sucesso e redireciona
    return True, "Cadastro realizado com sucesso!"

def pos_login(request):
    print("***\t POS LOGIN \t***")
    print("request.user:", request.user)
    print("request.user.is_authenticated:", request.user.is_authenticated)
    print("session usuario_id:", request.session.get('usuario_id'))

    # Verifica se o usuário está autenticado e se o usuario_id existe na sessão
    if request.user.is_authenticated:
        usuario_id = request.session.get('usuario_id')

        if usuario_id:
            try:
                usuario = Usuario.objects.get(id=usuario_id)
                print("usuario encontrado:", usuario.email, usuario.tipo)

                request.session['usuario_id'] = usuario.id
                request.session['usuario_tipo'] = usuario.tipo
                request.session['usuario_nome'] = request.user.first_name + " " + request.user.last_name

                # Se o tipo do usuário já está definido, redireciona para a home
                if usuario.tipo:
                    print("Enviando para home")
                    return redirect('home')
                else:
                    return redirect('cadastro_google')

            except Usuario.DoesNotExist:
                print("Usuario não encontrado")
                return redirect('login')
        else:
            return redirect('login')
    else:
        return redirect('login')
      
def cadastro_google_view(request):
    # Verifica se o usuário já está autenticado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')  # Se não tiver usuario_id, redireciona para login

    usuario = Usuario.objects.get(id=usuario_id)

    # Se o usuário já tiver um tipo (Cliente ou Barbeiro), redireciona para home
    if usuario.tipo:
        return redirect('home')

    nome_google = request.user.first_name + " " + request.user.last_name
    print(f"Nome = {nome_google}")

    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
            data['usuario_id'] = usuario_id
            data['nome_google'] = nome_google
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'JSON inválido'}, status=400)

        success, msg = cadastro_google(data)

        return JsonResponse({
            'success': success,
            'message': msg,
            'redirect_url': '/home' if success else ''
        })

    # Caso seja GET, apenas renderiza o formulário normalmente    
    return render(request, 'Projeto/cadastro_google.html')

def cadastro_google(data):
    tipo = data.get('tipo')
    usuario_id = data.get('usuario_id')
    nome = data.get('nome_google')
    telefone = data.get('telefone')
    data_nascimento = data.get('data_nascimento')
    cidade = data.get('cidade')
    cpf = data.get('cpf')
    
    usuario = Usuario.objects.get(id=usuario_id)
    usuario.tipo = tipo
    usuario.save()

    # Cria o perfil correspondente
    if tipo == 'Cliente':
        cliente = Cliente(
            nome=nome,
            id=usuario,
            cpf=cpf,
            telefone=telefone,
            data_nascimento=data_nascimento,
            cidade=cidade
        )
        cliente.save()

        return True, "Cadastro realizado com sucesso!"

    elif tipo == 'Barbeiro':
        barbeiro = Barbeiro(
            id=usuario,
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            data_nascimento=data_nascimento,
            cidade=cidade
        )
        barbeiro.save()

        return True, "Cadastro realizado com sucesso!"

    return False, "Erro no cadastro!"

def recuperar_senha_view(request):
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Json inválido'}, status=400)
                
        success, msg = recuperar_senha(data)

        if success:
            return JsonResponse({'success': success, 'message': msg})

    # Caso seja GET, apenas renderiza o formulário normalmente
    return render(request, 'Projeto/recuperar_senha.html')

def gerar_senha_temporaria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=tamanho))

def recuperar_senha(data):   
    email = data.get('email')

    try:
        usuario = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return False, "Email não encontrado"

    nova_senha = gerar_senha_temporaria()
    usuario.senha = make_password(nova_senha)
    usuario.save()

    if usuario.tipo == "Cliente":
        cliente = Cliente.objects.get(id=usuario.id)
        nome = cliente.nome
    elif usuario.tipo == "Barbeiro":
        barbeiro = Barbeiro.objects.get(id=usuario.id)
        nome = barbeiro.nome
    else:
        return False, "Tipo invalido"

    subject = 'Nova Senha Temporária'
    message = render_to_string('emails/reset_email.html', {
        'nome': nome,
        'nova_senha': nova_senha,
    })
    send_mail(subject, message, None, [usuario.email])

    return True, "Uma nova senha foi enviada para seu e-mail."

def home_view(request):
    print("Cheguei na home")
    # Recupera os dados da sessão
    usuario_id = request.session['usuario_id']
    tipo = request.session.get('usuario_tipo')
    nome = request.session.get('usuario_nome')

    print(f"ID = {usuario_id}; tipo = {tipo}; nome = {nome}")

    if not nome or not tipo:
        # Usuário não está logado, redireciona para login
        print("Voltando para o login")
        return redirect('login')

    # Defina ações diferentes dependendo do tipo de usuário
    if tipo == 'Cliente':
        
        acoes = ['Editar Perfil', 'Apagar Perfil', 'Inserir Agendamento', 'Ver Agendamentos']
    elif tipo == 'Barbeiro':
        acoes = ['Editar Perfil', 'Apagar Perfil', 'Cadastrar Local', 'Cadastrar Serviços',
                  'Cadastrar Horarios', 'Editar Local', 'Apagar Local', 'Gerenciar Agenda']
    else:
        acoes = []

    return render(request, 'Projeto/home.html', {
        'nome': nome,
        'tipo': tipo,
        'acoes': acoes,
    })

def editar_perfil_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']

    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        data['usuario_id'] = usuario_id

        resultado = editar_perfil(data)
        return JsonResponse({'success': resultado['status'] == 'success', 'message': resultado.get('message', '')})

    # Se for GET, busca os dados com a função auxiliar
    resultado = recuperar_dados_perfil(usuario_id)

    if resultado['status'] == 'success':
        return render(request, 'Projeto/usuario_editar_perfil.html', {
            'usuario': resultado['usuario'],
            'perfil': resultado['perfil']
        })
    else:
        return redirect('login')
    
def recuperar_dados_perfil(usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)

        if usuario.tipo == 'Cliente':
            perfil = Cliente.objects.get(id=usuario)
        elif usuario.tipo == 'Barbeiro':
            perfil = Barbeiro.objects.get(id=usuario)
        else:
            perfil = None  # Para tipo Admin, por exemplo

        return {
            'status': 'success',
            'usuario': usuario,
            'perfil': perfil
        }

    except Usuario.DoesNotExist:
        return {
            'status': 'error',
            'message': 'Usuário não encontrado'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def editar_perfil(data):
    try:
        usuario = Usuario.objects.get(id=data['usuario_id'])

        if usuario.tipo == 'Cliente':
            perfil = Cliente.objects.get(id=usuario)
        elif usuario.tipo == 'Barbeiro':
            perfil = Barbeiro.objects.get(id=usuario)
        else:
            return {'status': 'error', 'message': 'Tipo de usuário inválido'}

        # Atualiza o usuário
        usuario.email = data['email']
        if data['senha']:
            usuario.senha = make_password(data['senha'])
        usuario.save()

        # Atualiza o perfil
        perfil.nome = data['nome']
        perfil.telefone = data['telefone']
        perfil.cidade = data['cidade']
        perfil.save()

        return {'status': 'success'}

    except Usuario.DoesNotExist:
        return {'status': 'error', 'message': 'Usuário não encontrado'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def deletar_perfil_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']

    if request.method == 'POST':
        data = {'usuario_id': usuario_id}
        resultado = deletar_perfil(data)

        # Logout e redireciona
        request.session.flush()

        if resultado['status'] == 'success':
            return redirect('login')
        else:
            return render(request, 'Projeto/usuario_deletar_perfil.html', {'error': resultado['message']})

    return render(request, 'Projeto/usuario_deletar_perfil.html')

def deletar_perfil(data):
    usuario_id = data.get('usuario_id')
    try:
        usuario = Usuario.objects.get(id=usuario_id)

        if usuario.tipo == 'Cliente':
            cliente = Cliente.objects.get(id=usuario)
            Agenda.objects.filter(idcliente=cliente).delete()
            cliente.delete()

        elif usuario.tipo == 'Barbeiro':
            barbeiro = Barbeiro.objects.get(id=usuario)
            Agenda.objects.filter(idbarbeiro=barbeiro).delete()
            locais = Local.objects.filter(barbeirousuarioid=barbeiro)
            for local in locais:
                Servicos.objects.filter(idlocal=local).delete()
                Horarios.objects.filter(idlocal=local).delete()
                local.delete()

            barbeiro.delete()

        usuario.delete()

        return {'status': 'success'}

    except Usuario.DoesNotExist:
        return {'status': 'error', 'message': 'Usuário não encontrado'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def logout_view(request):
    request.session.flush()  # Limpa todos os dados da sessão
    return redirect('login')  # Redireciona para a página de login
