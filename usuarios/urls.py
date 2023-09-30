#usuarios/urls.py

from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=True), name='index'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('add_user/', views.add_user, name='add_user'),
    path('home/', views.home, name='home'),
    path('change_password/', views.change_password, name='change_password'),
    path('email_sent_notification/', views.email_sent_notification, name='email_sent_notification_page'),
    path('recuperar-senha/', views.password_recovery, name='password_recovery'),

    # URL para a página de editar/excluir usuários
    path('edit_delete_users/', views.edit_delete_users, name='edit_delete_users'),

    # Password Reset URLs provided by Django's auth_views
    path('accounts/', include('allauth.urls')),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Admin URL
    path('admin/', admin.site.urls),
]
