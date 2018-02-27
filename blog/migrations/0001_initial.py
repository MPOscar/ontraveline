# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-15 17:50
from __future__ import unicode_literals

import blog.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=128, unique=True, verbose_name='Nombre')),
                ('descripcion', models.CharField(max_length=255, verbose_name='Descripción')),
            ],
            options={
                'verbose_name_plural': 'Categorías',
            },
        ),
        migrations.CreateModel(
            name='Comentario_Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentario', models.TextField(max_length=32768, verbose_name='Comentario')),
                ('fecha_comentario', models.DateTimeField(auto_now_add=True, verbose_name='Fecha del Comentario')),
                ('en_respuesta_a', models.IntegerField(blank=True, null=True, verbose_name='En respuesta a (ID del Comentario)')),
                ('editado', models.BooleanField(default=False, verbose_name='Editado')),
            ],
            options={
                'verbose_name_plural': 'Comentarios Posts',
            },
        ),
        migrations.CreateModel(
            name='Foto_Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(blank=True, null=True, upload_to=blog.models.posts_photos_directory, verbose_name='Foto Servicio')),
            ],
        ),
        migrations.CreateModel(
            name='Galeria_Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('en_uso', models.BooleanField(default=True, verbose_name='En uso')),
            ],
            options={
                'verbose_name_plural': 'Galerías del Blog',
            },
        ),
        migrations.CreateModel(
            name='Like_Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_like', models.DateTimeField(auto_now_add=True, verbose_name='Fecha del Like')),
            ],
            options={
                'verbose_name_plural': 'Likes',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255, unique=True, verbose_name='Título')),
                ('descripcion', models.CharField(max_length=1024, verbose_name='Descripción')),
                ('texto', models.TextField(max_length=32768, verbose_name='Texto')),
                ('fecha_post', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
            ],
            options={
                'verbose_name_plural': 'Posts',
            },
        ),
        migrations.CreateModel(
            name='Video_Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(blank=True, max_length=64, null=True, verbose_name='Título')),
                ('descripcion', models.CharField(blank=True, max_length=256, null=True, verbose_name='Descripción')),
                ('url', models.URLField(max_length=128, unique=True, verbose_name='URL')),
            ],
            options={
                'verbose_name_plural': 'Videos de Posts',
            },
        ),
        migrations.CreateModel(
            name='Vista_Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_vista', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de la Vista')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='blog.Post')),
            ],
            options={
                'verbose_name_plural': 'Vistas Posts',
            },
        ),
    ]
