# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-15 17:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import servicios.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alojamiento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acceso_discapacitados', models.BooleanField(default=False, verbose_name='Acceso para Discapacitados')),
                ('cantidad_habitaciones', models.IntegerField(verbose_name='Cantidad de Habitaciones')),
                ('codigo_postal', models.CharField(max_length=8, verbose_name='Código Postal')),
                ('desayuno_cena', models.BooleanField(default=False, verbose_name='Desayuno/Cena')),
                ('direccion', models.CharField(max_length=128, verbose_name='Dirección Alojamiento')),
                ('latitud_gmaps', models.CharField(blank=True, max_length=32, null=True, verbose_name='Latitud GMaps')),
                ('longitud_gmaps', models.CharField(blank=True, max_length=32, null=True, verbose_name='Longitud GMaps')),
                ('internet', models.BooleanField(verbose_name='Internet')),
                ('patio_terraza_balcon', models.BooleanField(verbose_name='Patio/Terraza/Balcón')),
                ('parqueo', models.BooleanField(verbose_name='Parqueo')),
                ('permitido_fumar', models.BooleanField(verbose_name='Permitido Fumar')),
                ('permitido_mascotas', models.BooleanField(verbose_name='Permitido Mascotas')),
                ('permitido_ninnos', models.BooleanField(default=False, verbose_name='Permitido Niños')),
                ('piscina', models.BooleanField(default=False, verbose_name='Piscina')),
                ('por_habitacion', models.BooleanField(default=True, verbose_name='Por Habitación')),
                ('transporte_aeropuerto', models.BooleanField(verbose_name='Transporte al Aeropuerto')),
            ],
            options={
                'verbose_name_plural': 'Alojamientos',
            },
        ),
        migrations.CreateModel(
            name='Alojamiento_Completo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aire_acondicionado_central', models.BooleanField(default=False, verbose_name='Aire Acondicionado Central')),
                ('cantidad_bannos', models.IntegerField(verbose_name='Cantidad de Baños')),
                ('capacidad', models.IntegerField(verbose_name='Capacidad')),
                ('cocina', models.BooleanField(default=False, verbose_name='Cocina')),
                ('estereo', models.BooleanField(default=False, verbose_name='Estéreo')),
                ('lavadora', models.BooleanField(default=False, verbose_name='Lavadora')),
                ('nevera_bar', models.BooleanField(default=False, verbose_name='Nevera/Bar')),
                ('tv', models.BooleanField(default=False, verbose_name='TV')),
            ],
            options={
                'verbose_name_plural': 'Alojamientos Completos',
            },
        ),
        migrations.CreateModel(
            name='Alojamiento_sin_finalizar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acceso_discapacitados', models.BooleanField(default=False, verbose_name='Acceso para Discapacitados')),
                ('cantidad_habitaciones', models.IntegerField(blank=True, null=True, verbose_name='Cantidad de Habitaciones')),
                ('codigo_postal', models.CharField(blank=True, max_length=8, null=True, verbose_name='Código Postal')),
                ('desayuno_cena', models.BooleanField(default=False, verbose_name='Desayuno/Cena')),
                ('descripcion', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Descripción')),
                ('direccion', models.CharField(blank=True, max_length=128, null=True, verbose_name='Dirección')),
                ('latitud', models.CharField(blank=True, max_length=32, null=True, verbose_name='Latitud GMaps')),
                ('longitud', models.CharField(blank=True, max_length=32, null=True, verbose_name='Longitud GMaps')),
                ('internet', models.BooleanField(default=False, verbose_name='Internet')),
                ('nombre', models.CharField(blank=True, max_length=64, null=True, verbose_name='Nombre')),
                ('parqueo', models.BooleanField(default=False, verbose_name='Parqueo')),
                ('patio_terraza_balcon', models.BooleanField(default=False, verbose_name='Patio/Terraza/Balcón')),
                ('permitido_fumar', models.BooleanField(default=False, verbose_name='Permitido Fumar')),
                ('permitido_mascotas', models.BooleanField(default=False, verbose_name='Permitido Mascotas')),
                ('permitido_ninnos', models.BooleanField(default=False, verbose_name='Permitido Niños')),
                ('piscina', models.BooleanField(default=False, verbose_name='Piscina')),
                ('por_habitacion', models.BooleanField(default=True, verbose_name='Por Habitación')),
                ('transporte_aeropuerto', models.BooleanField(default=False, verbose_name='Transporte Aeropuerto')),
            ],
            options={
                'verbose_name_plural': 'Alojamientos sin finalizar',
            },
        ),
        migrations.CreateModel(
            name='Cancelacion_Reserva',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora de Cancelación')),
                ('motivo', models.CharField(max_length=255, verbose_name='Motivo de Cancelación')),
                ('cantidad_reembolso_euros', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Cantidad Reembolsada (€)')),
            ],
            options={
                'verbose_name_plural': 'Cancelación de Reservas',
            },
        ),
        migrations.CreateModel(
            name='CityTour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hora_inicio', models.TimeField(blank=True, null=True, verbose_name='Hora de Inicio')),
                ('hora_fin', models.TimeField(blank=True, null=True, verbose_name='Hora de Fin')),
            ],
            options={
                'verbose_name_plural': 'CityTours',
            },
        ),
        migrations.CreateModel(
            name='Comision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Precio')),
                ('comision', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Comisión')),
            ],
            options={
                'verbose_name_plural': 'Comisiones',
            },
        ),
        migrations.CreateModel(
            name='Destino',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=64, unique=True, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripcion')),
            ],
            options={
                'verbose_name_plural': 'Destinos',
            },
        ),
        migrations.CreateModel(
            name='Estado_Servicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(max_length=32, unique=True, verbose_name='Estado del Servicio')),
                ('descripcion', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name_plural': 'Posibles Estados de los Servicios',
            },
        ),
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(blank=True, max_length=64, null=True, verbose_name='Título')),
                ('evaluacion', models.IntegerField(default=0, verbose_name='Evaluación')),
                ('comentario', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Comentario')),
                ('fecha', models.DateTimeField(auto_now_add=True, verbose_name='Fecha')),
            ],
            options={
                'verbose_name_plural': 'Evaluaciones',
            },
        ),
        migrations.CreateModel(
            name='Excursion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hora_inicio', models.TimeField(blank=True, null=True, verbose_name='Hora de Inicio')),
                ('hora_fin', models.TimeField(blank=True, null=True, verbose_name='Hora de Fin')),
            ],
            options={
                'verbose_name_plural': 'Excursiones',
            },
        ),
        migrations.CreateModel(
            name='Favorito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True, verbose_name='Fecha de Registro')),
            ],
            options={
                'verbose_name_plural': 'Favoritos',
            },
        ),
        migrations.CreateModel(
            name='Foto_Destino',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(blank=True, null=True, upload_to=servicios.models.destinations_photos_directory, verbose_name='Foto Servicio')),
            ],
            options={
                'verbose_name_plural': 'Fotos de Destinos',
            },
        ),
        migrations.CreateModel(
            name='Foto_Habitacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(blank=True, null=True, upload_to=servicios.models.rooms_photos_directory, verbose_name='Foto Habitacion')),
            ],
            options={
                'verbose_name_plural': 'Fotos de Habitaciones',
            },
        ),
        migrations.CreateModel(
            name='Foto_Servicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(blank=True, null=True, upload_to=servicios.models.services_photos_directory, verbose_name='Foto Servicio')),
            ],
            options={
                'verbose_name_plural': 'Fotos de Servicios',
            },
        ),
        migrations.CreateModel(
            name='Habitacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agua_caliente', models.BooleanField(verbose_name='Agua Caliente')),
                ('aire_acondicionado', models.BooleanField(verbose_name='Aire Acondicionado')),
                ('balcon', models.BooleanField(verbose_name='Balcón')),
                ('caja_fuerte', models.BooleanField(verbose_name='Caja Fuerte')),
                ('camas_dobles', models.IntegerField(verbose_name='Camas Dobles')),
                ('camas_individuales', models.IntegerField(verbose_name='Camas Individuales')),
                ('estereo', models.BooleanField(verbose_name='Estéreo')),
                ('max_fotos', models.IntegerField(default=5, verbose_name='Máximo de fotos permitidas')),
                ('nevera_bar', models.BooleanField(verbose_name='Nevera/Bar')),
                ('tv', models.BooleanField(verbose_name='TV')),
                ('ventanas', models.BooleanField(verbose_name='Ventanas')),
                ('cerrada', models.BooleanField(default=False, verbose_name='Cerrada')),
            ],
            options={
                'verbose_name_plural': 'Habitaciones',
            },
        ),
        migrations.CreateModel(
            name='Habitacion_Alojamiento_Por_Habitacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banno_independiente', models.BooleanField(verbose_name='Baño Independiente')),
                ('capacidad', models.IntegerField(default=3, verbose_name='Capacidad')),
                ('precio_base', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Precio por Noche')),
            ],
            options={
                'verbose_name_plural': 'Habitaciones de Alojamientos por Habitación',
            },
        ),
        migrations.CreateModel(
            name='Idioma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=32, verbose_name='Nombre')),
                ('codigo', models.CharField(blank=True, max_length=3, null=True, verbose_name='Código')),
            ],
            options={
                'verbose_name_plural': 'Idiomas',
            },
        ),
        migrations.CreateModel(
            name='Indisponibilidad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_desde', models.DateField(verbose_name='Fecha Inicio')),
                ('fecha_hasta', models.DateField(verbose_name='Fecha Fin')),
            ],
            options={
                'verbose_name_plural': 'Indisponibilidades de Alojamientos',
            },
        ),
        migrations.CreateModel(
            name='Interes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=64, unique=True, verbose_name='Interés')),
            ],
            options={
                'verbose_name_plural': 'Intereses',
            },
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=64, unique=True, verbose_name='Nombre')),
                ('descripcion', models.CharField(max_length=1024, verbose_name='Descripción')),
            ],
            options={
                'verbose_name_plural': 'Marcas',
            },
        ),
        migrations.CreateModel(
            name='Moneda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_iso', models.CharField(max_length=3, verbose_name='Código ISO')),
                ('menu', models.BooleanField(default=False, verbose_name='Mostrar en Menú')),
            ],
            options={
                'verbose_name_plural': 'Monedas',
            },
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=32, verbose_name='Municipio')),
                ('descripcion', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name_plural': 'Municipios',
            },
        ),
        migrations.CreateModel(
            name='Pack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Packs',
            },
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=128, unique=True, verbose_name='País')),
                ('union_europea', models.BooleanField(default=False, verbose_name='Unión Europea')),
                ('prefijo_movil', models.CharField(blank=True, max_length=8, null=True, verbose_name='Prefijo Móvil')),
                ('codigo_iso_alfa2', models.CharField(blank=True, max_length=2, null=True, verbose_name='Código ISO Alfa-2')),
                ('codigo_iso_alfa3', models.CharField(blank=True, max_length=10, null=True, verbose_name='Código ISO Alfa-3')),
                ('codigo_iso_numerico', models.CharField(blank=True, max_length=8, null=True, verbose_name='Código ISO Numérico')),
            ],
            options={
                'verbose_name_plural': 'Países',
            },
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=128, verbose_name='Provincia')),
                ('descripcion', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name_plural': 'Provincias',
            },
        ),
        migrations.CreateModel(
            name='Recorrido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pax', models.IntegerField(verbose_name='Pax')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Precio')),
            ],
            options={
                'verbose_name_plural': 'Recorrido',
            },
        ),
        migrations.CreateModel(
            name='Regla_Cancelacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mas_de_x_dias', models.IntegerField(blank=True, null=True, verbose_name='Más de (X) días de antelación')),
                ('menos_de_x_dias', models.IntegerField(blank=True, null=True, verbose_name='Menos de (X) días de antelación')),
                ('porciento_devolucion', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Porciento de Devolución de la Pre-Reserva')),
            ],
            options={
                'verbose_name_plural': 'Reglas de Cancelación',
            },
        ),
        migrations.CreateModel(
            name='Regla_Precio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_desde', models.CharField(max_length=10, verbose_name='Desde')),
                ('fecha_hasta', models.CharField(max_length=10, verbose_name='Hasta')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Precio')),
                ('activa', models.BooleanField(default=True, verbose_name='Activa')),
            ],
            options={
                'verbose_name_plural': 'Reglas de Precio',
            },
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_date', models.DateField(verbose_name='Fecha de Inicio')),
                ('final_date', models.DateField(verbose_name='Fecha de Fin')),
                ('precio_servicio', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Precio')),
                ('comision', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Comisión')),
                ('fecha_creacion', models.DateField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('ninnos', models.IntegerField(blank=True, null=True, verbose_name='Niños')),
                ('adultos', models.IntegerField(blank=True, null=True, verbose_name='Adultos')),
                ('codigo_reserva', models.CharField(blank=True, max_length=255, null=True, verbose_name='Código de Reserva')),
            ],
            options={
                'verbose_name_plural': 'Reservas de Servicios',
            },
        ),
        migrations.CreateModel(
            name='Reserva_Habitacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ninnos', models.IntegerField(blank=True, null=True, verbose_name='Niños')),
                ('adultos', models.IntegerField(blank=True, null=True, verbose_name='Adultos')),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Precio')),
                ('comision', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Comisión')),
            ],
            options={
                'verbose_name_plural': 'Reservas de Habitaciones',
            },
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=64, verbose_name='Nombre')),
                ('descripcion', models.CharField(max_length=1024, verbose_name='Descripción')),
                ('email', models.EmailField(blank=True, max_length=64, null=True, verbose_name='E-Mail Servicio')),
                ('movil', models.CharField(blank=True, max_length=16, null=True, verbose_name='Móvil')),
                ('sitio_web', models.URLField(blank=True, max_length=128, null=True, verbose_name='Sitio Web')),
                ('max_fotos', models.IntegerField(default=8, verbose_name='Máximo de Fotos permitidas')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('precio_base', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Precio Base')),
                ('url_video', models.URLField(blank=True, max_length=255, null=True, verbose_name='URL Video')),
                ('destacado', models.BooleanField(default=False, verbose_name='Destacado')),
                ('cerrado', models.BooleanField(default=False, verbose_name='Cerrado')),
                ('visualizaciones', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Visualizaciones')),
                ('moneda', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='servicios.Moneda')),
            ],
            options={
                'verbose_name_plural': 'Servicios',
            },
        ),
        migrations.CreateModel(
            name='Taxi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modelo', models.CharField(blank=True, max_length=32, null=True, verbose_name='Modelo')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Precio diario')),
                ('marca', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='servicios.Marca')),
                ('servicio', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='servicios.Servicio')),
            ],
            options={
                'verbose_name_plural': 'Taxis',
            },
        ),
        migrations.CreateModel(
            name='Tipo_Alojamiento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=64, unique=True, verbose_name='Tipo de Alojamiento')),
            ],
            options={
                'verbose_name_plural': 'Tipos de Alojamientos',
            },
        ),
        migrations.CreateModel(
            name='Tipo_Cambio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_cambio', models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Tipo de Cambio')),
                ('moneda_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moneda_1', to='servicios.Moneda')),
                ('moneda_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moneda_2', to='servicios.Moneda')),
            ],
            options={
                'verbose_name_plural': 'Tipos de Cambio',
            },
        ),
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duracion_dias', models.IntegerField(verbose_name='Duración en días')),
                ('recorrido', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='servicios.Recorrido')),
            ],
            options={
                'verbose_name_plural': 'Tours',
            },
        ),
    ]