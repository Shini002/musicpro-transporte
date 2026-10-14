import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conductor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre del Conductor')),
                ('patente', models.CharField(max_length=20, verbose_name='Patente del Vehículo')),
                ('capacidad_kg', models.FloatField(verbose_name='Capacidad Máxima (kg)')),
                ('activo', models.BooleanField(default=True, verbose_name='Conductor Activo')),
            ],
            options={
                'verbose_name': 'Conductor',
                'verbose_name_plural': 'Conductores',
            },
        ),
        migrations.CreateModel(
            name='Despacho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(db_index=True, max_length=50, verbose_name='Código de Despacho')),
                ('origen', models.CharField(default='Bodega Central Providencia', max_length=150, verbose_name='Bodega de Origen')),
                ('destino', models.CharField(max_length=150, verbose_name='Sucursal de Destino')),
                ('peso_kg', models.FloatField(verbose_name='Peso de Carga (kg)')),
                ('estado', models.CharField(choices=[('En Preparación', 'En Preparación'), ('En Tránsito', 'En Tránsito'), ('Incidencia', 'Incidencia'), ('Entregado', 'Entregado')], default='En Preparación', max_length=30, verbose_name='Estado del Envío')),
                ('prioridad', models.CharField(choices=[('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta')], default='Media', max_length=20, verbose_name='Prioridad')),
                ('eta', models.CharField(default='Por coordinar', max_length=50, verbose_name='Tiempo Estimado (ETA)')),
                ('conductor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='despachos', to='logistica.conductor', verbose_name='Conductor Asignado')),
            ],
            options={
                'verbose_name': 'Despacho',
                'verbose_name_plural': 'Despachos',
            },
        ),
        migrations.CreateModel(
            name='ItemCarga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=200, verbose_name='Instrumento / Equipos')),
                ('cantidad', models.PositiveIntegerField(default=1, verbose_name='Cantidad de Unidades')),
                ('despacho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items_carga', to='logistica.despacho', verbose_name='Despacho Asociado')),
            ],
            options={
                'verbose_name': 'Ítem de Carga',
                'verbose_name_plural': 'Ítems de Carga',
            },
        ),
    ]
