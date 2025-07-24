from django.shortcuts import redirect
from .models import Usuario

def save_usuario_personalizado(backend, user, response, *args, **kwargs):
    request = kwargs.get('request')

    usuario, created = Usuario.objects.get_or_create(
        email=user.email,
        defaults={'senha': None}  # Senha não é necessária no caso do Google
    )
    if request:
        request.session['usuario_id'] = usuario.id
        # Adiciona o ID do usuário na sessão diretamente após a criação ou obtenção

    # ⚠️ FORÇA o redirecionamento final para pos-login (sobrescreve o ?next=)
    request.session['next'] = '/pos-login'

def redirecionar_pos_login(backend, user, response, *args, **kwargs):
    request = kwargs.get('request')
    if request:
        next_url = request.session.pop('next', '/pos-login')
        return {'redirect': next_url}