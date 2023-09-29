#usuarios/utils.py

from django.core.mail import send_mail
from django.conf import settings


def send_temporary_password_email(user_email, temp_password):
    """
    Esta função envia um e-mail ao usuário com a senha provisória.
    """
    subject = 'Sua senha provisória'
    message = f'Sua senha provisória é: {temp_password}'
    from_email = settings.DEFAULT_FROM_EMAIL  # Usa o endereço padrão de envio definido nas configurações do Django

    send_mail(subject, message, from_email, [user_email])
