# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-15 17:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Impuesto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=16, unique=True, verbose_name='Nombre')),
                ('porciento', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Porciento')),
            ],
            options={
                'verbose_name_plural': 'Impuestos',
            },
        ),
    ]
