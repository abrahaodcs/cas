# Generated by Django 4.2.5 on 2023-09-28 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_customuser_senhaprovisoriadata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='Senha',
        ),
    ]
