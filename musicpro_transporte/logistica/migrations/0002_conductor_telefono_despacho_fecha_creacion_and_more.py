import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conductor',
            name='telefono',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono de Contacto'),
        ),
        migrations.AddField(
            model_name='despacho',
            name='fecha_creacion',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de Registro'),
        ),
        migrations.AddField(
            model_name='despacho',
            name='observaciones',
            field=models.TextField(blank=True, null=True, verbose_name='Observaciones de Ruta'),
        ),
    ]
