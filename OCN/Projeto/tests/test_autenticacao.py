import json
from django.test import TestCase, Client
from django.urls import reverse
from Projeto.models import Usuario, Cliente, Barbeiro
from django.contrib.auth.hashers import make_password
from datetime import date

class AutenticacaoTestCase(TestCase):
    databases = {'default'}

    def setUp(self):
        self.client = Client(HTTP_CONTENT_TYPE='application/json')

        # Usuário tipo Cliente
        self.usuario_cliente = Usuario.objects.create(
            email="cliente@teste.com",
            senha=make_password("cliente123"),
            tipo="Cliente"
        )
        Cliente.objects.create(
            id=self.usuario_cliente,
            nome="Cliente Teste",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            cidade="São Paulo",
            cpf="12345678900"
        )

        self.usuario_barbeiro = Usuario.objects.create(
            email="barbeiro@testepython.com",
            senha=make_password("barbeiro123"),
            tipo="Barbeiro"
        )
        Barbeiro.objects.create(
            id=self.usuario_barbeiro,
            nome="Barbeiro Teste",
            telefone="11944445555",
            data_nascimento=date(1992, 2, 2),
            cidade="Barbearia City",
            cpf="44455566677"
        )

    # Cadastro

    def test_1_1_cadastro_usuario_valido(self):
        url = reverse('cadastro')
        payload = {
            "nome": "Novo Usuário",
            "senha": "senha123",
            "tipo": "Cliente",
            "telefone": "11911112222",
            "data_nascimento": "1995-05-05",
            "email": "novo@teste.com",
            "cidade": "São Paulo",
            "cpf": "11122233344"
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("Cadastro realizado com sucesso", data["message"])
        print(response.status_code, response.content)

    def test_1_2_cadastro_usuario_email_duplicado(self):
        url = reverse('cadastro')
        payload = {
            "nome": "Duplicado",
            "senha": "senha123",
            "tipo": "Cliente",
            "telefone": "11888888888",
            "data_nascimento": "1990-01-01",
            "email": "cliente@teste.com",  # Já existe
            "cidade": "São Paulo",
            "cpf": "99999999999"
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("Email já cadastrado", data["message"])
        print(response.status_code, response.content)

    def test_1_5_cadastro_campos_vazios(self):
        url = reverse('cadastro')
        payload = {
            "nome": "",
            "senha": "",
            "tipo": "Cliente",
            "telefone": "",
            "data_nascimento": "",
            "email": "",
            "cidade": "",
            "cpf": ""
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("Preencha todos os campos", data["message"])
        print(response.status_code, response.content)

    # Login

    def test_1_3_login_cliente_valido(self):
        url = reverse('login')
        payload = {
            "email": "cliente@teste.com",
            "senha": "cliente123"
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["redirect_url"], "/home")
        print(response.status_code, response.content)

    def test_1_6_login_barbeiro_valido(self):
        url = reverse('login')
        payload = {
            "email": "barbeiro@testepython.com",
            "senha": "barbeiro123"
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["redirect_url"], "/home")
        print(response.status_code, response.content)

    def test_1_4_login_usuario_invalido(self):
        url = reverse('login')
        payload = {
            "email": "naoexiste@teste.com",
            "senha": "senhaincorreta"
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["redirect_url"], "")
        self.assertIn("Usuario não encontrado", data["message"])
        print(response.status_code, response.content)

    def test_1_7_login_senha_incorreta(self):
        url = reverse('login')
        payload = {
            "email": "cliente@teste.com",
            "senha": "errada123"
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["redirect_url"], "")
        self.assertIn("Senha incorreta", data["message"])
        print(response.status_code, response.content)

    def test_1_8_login_campo_vazio(self):
        url = reverse('login')
        payload = {
            "email": "",
            "senha": ""
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["redirect_url"], "")
        self.assertIn("Preencha todos os campos", data["message"])
        print(response.status_code, response.content)
