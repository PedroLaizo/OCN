from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('cadastro-google/', views.cadastro_google_view, name='cadastro_google'),
    path('pos-login/', views.pos_login, name='pos_login'),
    path('recuperar-senha', views.recuperar_senha_view, name='recuperar_senha'),
    path('home/', views.home_view, name='home'),
    path('meu-perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    path('meu-perfil/deletar/', views.deletar_perfil_view, name='deletar_perfil'),
    path('logout/', views.logout_view, name='logout'),
]