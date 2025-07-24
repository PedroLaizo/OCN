from django.db import models

# Definição dos tipos ENUM para Django
class TipoUsuario(models.TextChoices):
    CLIENTE = 'Cliente', 'Cliente'
    BARBEIRO = 'Barbeiro', 'Barbeiro'
    ADMIN = 'Admin', 'Admin'

class Usuario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)   
    email = models.CharField(db_column='Email', max_length=255, blank=True, null=True)         
    senha = models.CharField(db_column='Senha', max_length=255, blank=True, null=True)         
    tipo = models.TextField(db_column='Tipo', blank=True, null=True)   

    class Meta:
        managed = False
        db_table = 'Usuario'

class Cliente(models.Model):
    id = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='ID', primary_key=True)   
    cpf = models.CharField(db_column='CPF', max_length=14, blank=True, null=True)   
    nome = models.CharField(db_column='Nome', max_length=255, blank=True, null=True)           
    cidade = models.CharField(db_column='Cidade', max_length=255, blank=True, null=True)       
    telefone = models.CharField(db_column='Telefone', max_length=16, blank=True, null=True)    
    data_nascimento = models.DateField(db_column='Data_Nascimento', blank=True, null=True)     

    class Meta:
        managed = False
        db_table = 'Cliente'

class Barbeiro(models.Model):
    id = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='ID', primary_key=True)   
    nome = models.CharField(db_column='Nome', max_length=255, blank=True, null=True)           
    cpf = models.CharField(db_column='CPF', max_length=14, blank=True, null=True)   
    telefone = models.CharField(db_column='Telefone', max_length=16, blank=True, null=True)    
    data_nascimento = models.DateField(db_column='Data_Nascimento', blank=True, null=True)     
    cidade = models.CharField(db_column='Cidade', max_length=255, blank=True, null=True)       

    class Meta:
        managed = False
        db_table = 'Barbeiro'

