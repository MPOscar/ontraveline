# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-15 17:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aeropuerto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_iata', models.CharField(db_index=True, max_length=5, unique=True, verbose_name='Código IATA')),
                ('info_completa', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nombre')),
                ('cuba', models.BooleanField(default=False, verbose_name='Cuba')),
            ],
            options={
                'verbose_name_plural': 'Aeropuertos',
            },
        ),
        migrations.CreateModel(
            name='Mensaje_Contacto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=64, null=True, verbose_name='Nombre')),
                ('email', models.EmailField(max_length=64, verbose_name='E-Mail')),
                ('message', models.CharField(max_length=1024, verbose_name='Mensaje')),
            ],
            options={
                'verbose_name_plural': 'Mensajes de Contacto',
            },
        ),
        migrations.CreateModel(
            name='Testimonio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testimonio', models.CharField(max_length=255, verbose_name='Testimonio')),
                ('mostrar', models.BooleanField(default=False, verbose_name='Mostrar')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.Usuario')),
            ],
            options={
                'verbose_name_plural': 'Testimonios',
            },
        ),
    ]
