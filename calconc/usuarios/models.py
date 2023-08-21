from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

# from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UsuarioManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        # extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True')

        return self._create_user(email, password, **extra_fields)


class CustomUsuario(AbstractUser):
    email = models.EmailField('E-mail', unique=True)
    fone = models.CharField('Telefone', max_length=15)
    is_staff = models.BooleanField('Membro da equipe', default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'fone']

    def _str_(self):
        return self.email

    objects = UsuarioManager()

class Fornecedor(models.Model):
    nome = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100)
    id = models.CharField(max_length=18, primary_key=True)
    bairro = models.CharField(max_length=200)
    logradouro = models.CharField(max_length=100)
    CEP = models.CharField(max_length=18)
    complemento = models.CharField(max_length=200)
    cpf_cnpj = models.CharField(max_length=20)
    fone_1 = models.CharField(max_length=100)
    ie = models.CharField(max_length=18)
    observacao = models.CharField(max_length=20)
    def __str__(self):
        return self.nome

class TipoAgregado(models.Model):
    nome = models.CharField(max_length=20)
    def __str__(self):
        return self.nome

def positive_float_field():
    return models.FloatField(null=False, unique=False, validators=[MinValueValidator(0.00001)])

class Agregado(models.Model):
    nome = models.CharField(max_length=20, unique=True)
    pen_6_30_mm = models.FloatField()
    pen_4_80_mm = models.FloatField()
    pen_2_40_mm = models.FloatField()
    pen_1_20_mm = models.FloatField()
    pen_600_um = models.FloatField()
    pen_300_um = models.FloatField()
    pen_150_um = models.FloatField()
    pen_75_um = models.FloatField()
    fundo = models.FloatField()
    umidade = models.FloatField()
    massa_especifica = models.FloatField()
    is_deleted = models.BooleanField(default=False)
    fk_usuario_id = models.IntegerField()  # Você pode querer usar ForeignKey em vez de IntegerField
    num_modificacao = models.IntegerField(default=0)
    data_cadastro = models.DateTimeField(default=timezone.now)
    fk_fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    fk_tipo_agregado = models.ForeignKey(TipoAgregado, on_delete=models.CASCADE, related_name='agregados')
    def __str__(self):
        return self.nome

class Historico(models.Model):
    nome = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return  self.nome

class Traco(models.Model):
    nome = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return  self.nome

class Usuarios(models.Model):
    nome = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return  self.nome