# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-15 17:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import usuarios.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('servicios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Codigo_Recovery_Password',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=64, unique=True, verbose_name='Código')),
                ('valido', models.BooleanField(default=True, verbose_name='Válido')),
            ],
            options={
                'verbose_name_plural': 'Códigos de Recuperación de Contraseña de Usuarios',
            },
        ),
        migrations.CreateModel(
            name='Foto_Licencia_Actividad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(blank=True, null=True, upload_to=usuarios.models.activity_permission_photos_directory, verbose_name='Foto de Licencia de Actividad')),
            ],
            options={
                'verbose_name_plural': 'Fotos de Licencia de Actividad',
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_password', models.CharField(blank=True, max_length=32, null=True, verbose_name='Raw Password')),
                ('direccion', models.CharField(blank=True, max_length=128, null=True, verbose_name='Dirección')),
                ('ciudad', models.CharField(blank=True, max_length=64, null=True, verbose_name='Ciudad')),
                ('codigo_postal', models.CharField(blank=True, max_length=12, null=True, verbose_name='Código Postal')),
                ('movil', models.CharField(blank=True, max_length=16, null=True, verbose_name='Móvil')),
                ('proveedor', models.BooleanField(default=False, verbose_name='Es Proveedor de Servicios')),
                ('cerrado', models.BooleanField(default=False, verbose_name='Cuenta cerrada')),
                ('foto', models.ImageField(blank=True, null=True, upload_to=usuarios.models.user_directory_profile_photo, verbose_name='Foto')),
                ('fecha_creacion', models.DateField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('ultima_modificacion', models.DateField(auto_now=True, verbose_name='Última Modificación')),
                ('verificado_email', models.BooleanField(default=False, verbose_name='Verificado E-Mail')),
                ('verificado_movil', models.BooleanField(default=False, verbose_name='Verificado Móvil')),
                ('verificado_facebook', models.BooleanField(default=False, verbose_name='Verificado Facebook')),
                ('verificado_twitter', models.BooleanField(default=False, verbose_name='Verificado Twitter')),
                ('verificado_linkedin', models.BooleanField(default=False, verbose_name='Verificado Linkedin')),
                ('verificado_google', models.BooleanField(default=False, verbose_name='Verificado Google')),
                ('verificado_proveedor', models.BooleanField(default=False, verbose_name='Verificado Proveedor')),
                ('pais', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='servicios.Pais')),
                ('provincia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='servicios.Provincia')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Usuarios',
            },
        ),
        migrations.AddField(
            model_name='foto_licencia_actividad',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.Usuario'),
        ),
        migrations.AddField(
            model_name='codigo_recovery_password',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.Usuario'),
        ),
    ]
