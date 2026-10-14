from django.contrib import admin
from .models import Conductor, Despacho, ItemCarga

# Personalización general del encabezado de Django Admin
admin.site.site_header = "MusicPro Transporte - Administración"
admin.site.site_title = "Portal Admin MusicPro"
admin.site.index_title = "Gestión Logística de Despachos, Flota y Carga"


class ItemCargaInline(admin.TabularInline):
    model = ItemCarga
    extra = 1


@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'patente', 'capacidad_kg', 'telefono', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'patente', 'telefono')
    list_editable = ('activo',)
    list_per_page = 25


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'codigo',
        'origen',
        'destino',
        'conductor',
        'peso_kg',
        'estado',
        'prioridad',
        'eta',
        'fecha_creacion',
    )
    list_filter = ('estado', 'prioridad', 'origen', 'fecha_creacion')
    search_fields = ('codigo', 'destino', 'conductor__nombre', 'conductor__patente')
    list_editable = ('estado', 'prioridad')
    list_select_related = ('conductor',)
    list_per_page = 25
    inlines = [ItemCargaInline]


@admin.register(ItemCarga)
class ItemCargaAdmin(admin.ModelAdmin):
    list_display = ('id', 'despacho', 'descripcion', 'cantidad')
    list_filter = ('despacho__estado',)
    search_fields = ('descripcion', 'despacho__codigo')
    list_select_related = ('despacho',)
    list_per_page = 25