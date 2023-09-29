#usuarios/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import secrets
import string
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password


def generate_random_password(length=8):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


class CustomUserManager(BaseUserManager):
    def create_user(self, cpf, password=None, **extra_fields):
        if not cpf:
            raise ValueError('O CPF é obrigatório.')

        user = self.model(cpf=cpf, **extra_fields)
        user.set_password(password)
        user.initialize_temporary_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    cpf = models.CharField(max_length=11, unique=True, primary_key=True)
    senha_provisoria = models.CharField(max_length=512, blank=True, null=True)
    senha_provisoria_data = models.DateTimeField(blank=True, null=True)
    nome = models.CharField(max_length=255)
    cargo = models.CharField(max_length=50)
    nivel_acesso = models.CharField(max_length=50)
    nivel_organizacional = models.CharField(max_length=50)
    data_nascimento = models.DateField()
    data_ingresso = models.DateField()
    email = models.EmailField(max_length=225, unique=True)
    celular = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['nome', 'cargo', 'nivel_acesso', 'nivel_organizacional', 'data_nascimento', 'data_ingresso']

    def initialize_temporary_password(self):
        if not self.senha_provisoria:
            temp_password = generate_random_password()
            self.senha_provisoria = make_password(temp_password)
            self.senha_provisoria_data = timezone.now()

    def is_temporary_password_valid(self):
        if self.senha_provisoria_data:
            expiration_date = self.senha_provisoria_data + timedelta(hours=48)
            return timezone.now() < expiration_date
        return False

    def __str__(self):
        return self.cpf
