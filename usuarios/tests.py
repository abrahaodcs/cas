#usuarios/tests.py

from django.test import TestCase
from .models import CustomUser
from django.urls import reverse
from unittest import mock
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password

def fake_now():
    print("Fake now() chamado!")
    return timezone.now() + timedelta(hours=49)

class UserCreationTestCase(TestCase):
    def test_user_creation_with_temporary_password(self):
        user = CustomUser.objects.create_user(
            CPF="12345678901",
            password="samplepassword",
            SenhaProvisoria="sampletemp_password",
            Cargo="SampleCargo",
            NivelAcesso="SampleAccessLevel",
            NivelOrganizacional="SampleOrgLevel",
            Nome="Test User",
            DataNascimento="1990-01-01",
            DataIngresso="2022-01-01",
            Celular="1234567890"
        )
        self.assertTrue(user.SenhaProvisoria)


class UserLoginTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            CPF="12345678901",
            password="samplepassword",
            SenhaProvisoria=make_password("sampletemp_password"),
            SenhaProvisoriaData=timezone.now() - timedelta(hours=1),  # Garante que a senha temporária tenha apenas 1 hora de idade
            Cargo="SampleCargo",
            NivelAcesso="SampleAccessLevel",
            NivelOrganizacional="SampleOrgLevel",
            Nome="Test User",
            DataNascimento="1990-01-01",
            DataIngresso="2022-01-01",
            Celular="1234567890"
        )
        print("SenhProvisoriaData:", self.user.SenhaProvisoriaData)

    def test_user_login_with_temporary_password(self):
        response = self.client.post(reverse('user_login'), {
            'CPF': '12345678901',
            'password': 'sampletemp_password',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('change_password'))

    def test_user_login_fail_with_wrong_password(self):
        response = self.client.post(reverse('user_login'), {
            'CPF': '12345678901',
            'password': 'wrongpassword',
        })

        # Verificando a mensagem de erro
        self.assertContains(response, "Senha incorreta.")


class PasswordExpiryTestCase(TestCase):
    def test_temporary_password_expiry(self):
        user = CustomUser.objects.create_user(
            CPF="12345678901",
            password="samplepassword",
            SenhaProvisoria="sampletemp_password",
            SenhaProvisoriaData=timezone.now() - timedelta(hours=49),  # Defina isso diretamente aqui.
            Cargo="SampleCargo",
            NivelAcesso="SampleAccessLevel",
            NivelOrganizacional="SampleOrgLevel",
            Nome="Test User",
            DataNascimento="1990-01-01",
            DataIngresso="2022-01-01",
            Celular="1234567890"
        )
        self.assertFalse(user.is_temporary_password_valid())

class PasswordChangeTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            CPF="12345678901",
            password="samplepassword",
            SenhaProvisoria=make_password("sampletemp_password"),
            SenhaProvisoriaData=timezone.now() - timedelta(hours=1),  # Garante que a senha temporária tenha apenas 1 hora de idade
            Cargo="SampleCargo",
            NivelAcesso="SampleAccessLevel",
            NivelOrganizacional="SampleOrgLevel",
            Nome="Test User",
            DataNascimento="1990-01-01",
            DataIngresso="2022-01-01",
            Celular="1234567890"
        )
        self.client.force_login(self.user)

    def test_user_login_with_temporary_password(self):
        response = self.client.post(reverse('user_login'), {
            'CPF': '12345678901',
            'password': 'sampletemp_password',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('change_password'))


class TemporaryPasswordValidityTest(TestCase):

    def test_temp_password_validity_within_48_hours(self):
        user = CustomUser.objects.create_user(
            CPF="12345678901",
            SenhaProvisoriaData=timezone.now(),
            Nome="Test User",
            Cargo="SampleCargo",
            NivelAcesso="SampleAccessLevel",
            NivelOrganizacional="SampleOrgLevel",
            DataNascimento="1990-01-01",
            DataIngresso="2022-01-01",
            Celular="1234567890"
        )
        self.assertTrue(user.is_temporary_password_valid())

    def test_temp_password_invalidity_after_48_hours(self):
        user = CustomUser.objects.create_user(
            CPF="12345678901",
            SenhaProvisoriaData=timezone.now() - timedelta(hours=49),
            Nome="Test User",
            Cargo="SampleCargo",
            NivelAcesso="SampleAccessLevel",
            NivelOrganizacional="SampleOrgLevel",
            DataNascimento="1990-01-01",
            DataIngresso="2022-01-01",
            Celular="1234567890"
        )
        self.assertFalse(user.is_temporary_password_valid())

