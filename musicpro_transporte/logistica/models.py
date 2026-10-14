from django.db import models
from django.utils import timezone


class Conductor(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Conductor")
    patente = models.CharField(max_length=20, verbose_name="Patente del Vehículo")
    capacidad_kg = models.FloatField(verbose_name="Capacidad Máxima (kg)")
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono de Contacto"
    )
    activo = models.BooleanField(default=True, verbose_name="Conductor Activo")

    class Meta:
        verbose_name = "Conductor"
        verbose_name_plural = "Conductores"

    def __str__(self):
        return f"{self.nombre} ({self.patente} - Máx: {self.capacidad_kg} kg)"


class Despacho(models.Model):
    ESTADOS = [
        ('En Preparación', 'En Preparación'),
        ('En Tránsito', 'En Tránsito'),
        ('Incidencia', 'Incidencia'),
        ('Entregado', 'Entregado'),
    ]

    PRIORIDADES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]

    codigo = models.CharField(max_length=50, verbose_name="Código de Despacho", db_index=True)
    origen = models.CharField(
        max_length=150,
        default="Bodega Central Providencia",
        verbose_name="Bodega de Origen"
    )
    destino = models.CharField(max_length=150, verbose_name="Sucursal de Destino")
    conductor = models.ForeignKey(
        Conductor,
        on_delete=models.CASCADE,
        related_name="despachos",
        verbose_name="Conductor Asignado"
    )
    peso_kg = models.FloatField(verbose_name="Peso de Carga (kg)")
    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default='En Preparación',
        verbose_name="Estado del Envío"
    )
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDADES,
        default='Media',
        verbose_name="Prioridad"
    )
    eta = models.CharField(max_length=50, default="Por coordinar", verbose_name="Tiempo Estimado (ETA)")
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones de Ruta"
    )
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Registro"
    )

    class Meta:
        verbose_name = "Despacho"
        verbose_name_plural = "Despachos"

    def __str__(self):
        return f"{self.codigo} - {self.destino} ({self.estado})"


class ItemCarga(models.Model):
    despacho = models.ForeignKey(
        Despacho,
        on_delete=models.CASCADE,
        related_name="items_carga",
        verbose_name="Despacho Asociado"
    )
    descripcion = models.CharField(max_length=200, verbose_name="Instrumento / Equipos")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad de Unidades")

    class Meta:
        verbose_name = "Ítem de Carga"
        verbose_name_plural = "Ítems de Carga"

    def __str__(self):
        return f"{self.cantidad}x {self.descripcion} ({self.despacho.codigo})"