#usuarios/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, generate_random_password
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone


def send_temporary_password_email(email, password):
    send_mail(
        'Sua senha provisória',
        f'Sua senha provisória é: {password}',
        'noreply@yourdomain.com',
        [email],
        fail_silently=False,
    )


def email_sent_notification(request):
    context = {
        'message': 'Um e-mail com sua senha provisória foi enviado. Por favor, verifique sua caixa de entrada.'
    }
    return render(request, 'usuarios/email_sent_notification.html', context)


def user_login(request):
    if request.method == "POST":
        cpf = request.POST.get('CPF')
        password = request.POST.get('password')

        user = get_object_or_404(CustomUser, cpf=cpf)

        if user.check_password(password):
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('home')
        elif user.senha_provisoria and check_password(password, user.senha_provisoria):
            if user.is_temporary_password_valid():
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                return redirect('change_password')
            else:
                send_new_temp_password(user)
                return redirect('email_sent_notification_page')
        else:
            messages.error(request, 'Senha incorreta.')

    return render(request, 'usuarios/login.html')

def send_new_temp_password(user):
    new_temp_password = generate_random_password()
    user.senha_provisoria = make_password(new_temp_password)
    user.senha_provisoria_data = timezone.now()
    user.save()
    send_temporary_password_email(user.email, new_temp_password)


def add_user(request):
    if request.method == "POST":
        data = {
            'CPF': request.POST.get("cpf"),
            'password': request.POST.get("password"),
            'senha_provisoria': make_password(request.POST.get("senha_provisoria")),
            'cargo': request.POST.get("cargo"),
            'nivel_acesso': request.POST.get("nivel_acesso"),
            'nivel_organizacional': request.POST.get("nivel_organizacional"),
            'nome': request.POST.get("nome"),
            'data_nascimento': request.POST.get("data_nascimento"),
            'data_ingresso': request.POST.get("data_ingresso"),
            'celular': request.POST.get("celular")
        }

        CustomUser.objects.create(**data)
        return redirect('home')

    return render(request, 'usuarios/add_user.html')


def home(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    return render(request, 'usuarios/home.html')


def password_recovery(request):
    if request.method == "POST":
        cpf = request.POST.get('CPF')
        user = get_object_or_404(CustomUser, CPF=cpf)

        send_new_temp_password(user)

        messages.success(request, 'Uma senha provisória foi enviada para o seu email.')
        return redirect('user_login')

    return render(request, 'usuarios/password_recovery.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')


@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        user = request.user

        is_valid_password = user.check_password(old_password) or check_password(old_password, user.senha_provisoria)

        if is_valid_password:
            user.set_password(new_password)
            user.senha_provisoria = None
            user.save()
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Senha antiga não corresponde.')

    return render(request, 'usuarios/change_password.html')
