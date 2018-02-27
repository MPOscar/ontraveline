# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-15 17:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog', '0001_initial'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vista_post',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.Usuario'),
        ),
        migrations.AddField(
            model_name='video_post',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Post'),
        ),
        migrations.AddField(
            model_name='post',
            name='autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.Usuario'),
        ),
        migrations.AddField(
            model_name='post',
            name='categorias',
            field=models.ManyToManyField(blank=True, to='blog.Categoria'),
        ),
        migrations.AddField(
            model_name='like_post',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='blog.Post'),
        ),
        migrations.AddField(
            model_name='like_post',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.Usuario'),
        ),
        migrations.AddField(
            model_name='galeria_blog',
            name='fotos_posts',
            field=models.ManyToManyField(blank=True, to='blog.Foto_Post'),
        ),
        migrations.AddField(
            model_name='foto_post',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Post'),
        ),
        migrations.AddField(
            model_name='comentario_post',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='blog.Post'),
        ),
        migrations.AddField(
            model_name='comentario_post',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.Usuario'),
        ),
    ]
