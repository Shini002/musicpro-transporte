from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('despachos/', views.listar_despachos, name='despachos'),
    path('despachos/<int:id>/', views.detalle_despacho, name='detalle_despacho'),
    path('despachos/nuevo/', views.crear_despacho, name='nuevo_despacho'),
    path('despachos/editar/<int:id>/', views.editar_despacho, name='editar_despacho'),
    path('despachos/eliminar/<int:id>/', views.eliminar_despacho, name='eliminar_despacho'),
]