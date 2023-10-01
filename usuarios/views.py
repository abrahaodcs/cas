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
from django.db.models import Q
from django.http import HttpResponse
from .forms import EditUserForm
from django.contrib.auth.decorators import user_passes_test

def admin_check(user):
    return user.nivel_acesso == "Administrador"

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

def edit_delete_users(request):
    users = CustomUser.objects.all()  # Por padrão, mostramos todos os usuários
    selected_user = None  # Nenhum usuário selecionado por padrão

    # Verifica se um termo de busca foi fornecido
    search_term = request.GET.get('search', '')
    if search_term:
        # Filtra os usuários pelo termo de busca (nome ou CPF)
        users = users.filter(
            Q(cpf__icontains=search_term) | Q(nome__icontains=search_term)
        )

    # Verifica se um usuário foi selecionado para edição
    selected_cpf = request.GET.get('edit_cpf', None)
    if selected_cpf:
        try:
            selected_user = CustomUser.objects.get(cpf=selected_cpf)
        except CustomUser.DoesNotExist:
            # Aqui você pode manipular o erro conforme necessário, talvez redirecionar ou mostrar uma mensagem de erro
            pass

    return render(request, 'usuarios/edit_delete_users.html', {
        'users': users,
        'selected_user': selected_user,
    })

def edit_user(request, cpf):
    try:
        user = CustomUser.objects.get(cpf=cpf)
    except CustomUser.DoesNotExist:
        return HttpResponse("Usuário não encontrado", status=404)

    if request.method == "POST":
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Você pode redirecionar para a página que quiser após a edição bem-sucedida
            return redirect('edit_delete_users')
    else:
        form = EditUserForm(instance=user)

    return render(request, 'usuarios/edit_user.html', {
        'form': form,
        'user': user,
    })

@user_passes_test(admin_check, login_url='user_login')
def delete_user(request, cpf):
    user = get_object_or_404(CustomUser, cpf=cpf)

    if request.method == "POST":
        user.delete()
        return redirect('edit_delete_users')  # redireciona de volta para a lista de usuários

    return render(request, 'usuarios/confirm_delete.html', {'user': user})

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
