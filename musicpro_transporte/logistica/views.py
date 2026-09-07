import json
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

def _obtener_despachos():
    ruta = os.path.join(settings.BASE_DIR, 'data', 'despachos.json')
    if not os.path.exists(ruta):
        return []
    with open(ruta, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)

def _guardar_despachos(lista_despachos):
    ruta = os.path.join(settings.BASE_DIR, 'data', 'despachos.json')
    with open(ruta, 'w', encoding='utf-8') as archivo:
        json.dump(lista_despachos, archivo, indent=2, ensure_ascii=False)

def index(request):
    despachos = _obtener_despachos()
    en_transito = [d for d in despachos if d['estado'] == 'En Tránsito']
    incidencias = [d for d in despachos if d['estado'] == 'Incidencia']
    entregados = [d for d in despachos if d['estado'] == 'Entregado']
    
    contexto = {
        'total_despachos': len(despachos),
        'en_transito_count': len(en_transito),
        'incidencias_count': len(incidencias),
        'entregados_count': len(entregados),
        'ultimos_despachos': despachos[:5]
    }
    return render(request, 'logistica/index.html', contexto)

def listar_despachos(request):
    despachos = _obtener_despachos()
    filtro_estado = request.GET.get('estado', '')
    if filtro_estado:
        despachos = [d for d in despachos if d['estado'].lower() == filtro_estado.lower()]
        
    contexto = {
        'despachos': despachos,
        'filtro_activo': filtro_estado
    }
    return render(request, 'logistica/despachos.html', contexto)

def detalle_despacho(request, id):
    despachos = _obtener_despachos()
    despacho = next((d for d in despachos if d['id'] == id), None)
    return render(request, 'logistica/detalle.html', {'despacho': despacho})

def crear_despacho(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        destino = request.POST.get('destino', '').strip()
        conductor = request.POST.get('conductor', '').strip()
        patente = request.POST.get('patente', '').strip()
        peso = request.POST.get('peso', '').strip()
        capacidad = request.POST.get('capacidad', '').strip()

        if not all([codigo, destino, conductor, patente, peso, capacidad]):
            messages.error(request, "Todos los campos son obligatorios.")
        else:
            try:
                val_peso = float(peso)
                val_capacidad = float(capacidad)

                if val_peso <= 0:
                    messages.error(request, "El peso de la carga debe ser mayor a 0 kg.")
                elif val_peso > val_capacidad:
                    messages.warning(request, f"¡Alerta de Cubicaje! La carga ({val_peso} kg) supera la capacidad del vehículo ({val_capacidad} kg).")
                else:
                    despachos = _obtener_despachos()
                    nuevo_id = max([d['id'] for d in despachos], default=0) + 1
                    nuevo_registro = {
                        "id": nuevo_id,
                        "codigo": codigo,
                        "origen": "Bodega Central Providencia",
                        "destino": destino,
                        "conductor": conductor,
                        "patente": patente,
                        "peso_kg": val_peso,
                        "capacidad_kg": val_capacidad,
                        "estado": "En Preparación",
                        "prioridad": "Media",
                        "eta": "Por coordinar",
                        "carga": ["Lote inicial registrado desde formulario"]
                    }
                    despachos.append(nuevo_registro)
                    _guardar_despachos(despachos)
                    messages.success(request, f"Despacho {codigo} registrado exitosamente.")
                    return redirect('despachos')
            except ValueError:
                messages.error(request, "El peso y la capacidad deben ser valores numéricos válidos.")

    return render(request, 'logistica/nuevo.html')

def editar_despacho(request, id):
    despachos = _obtener_despachos()
    despacho = next((d for d in despachos if d['id'] == id), None)
    
    if not despacho:
        messages.error(request, "El despacho solicitado no existe.")
        return redirect('despachos')

    if request.method == 'POST':
        destino = request.POST.get('destino', '').strip()
        conductor = request.POST.get('conductor', '').strip()
        patente = request.POST.get('patente', '').strip()
        peso = request.POST.get('peso', '').strip()
        capacidad = request.POST.get('capacidad', '').strip()
        estado = request.POST.get('estado', '').strip()
        eta = request.POST.get('eta', '').strip()

        try:
            val_peso = float(peso)
            val_capacidad = float(capacidad)

            if val_peso > val_capacidad:
                messages.warning(request, f"¡Alerta! La carga ({val_peso} kg) supera la capacidad del móvil ({val_capacidad} kg).")
            else:
                despacho['destino'] = destino
                despacho['conductor'] = conductor
                despacho['patente'] = patente
                despacho['peso_kg'] = val_peso
                despacho['capacidad_kg'] = val_capacidad
                despacho['estado'] = estado
                despacho['eta'] = eta

                _guardar_despachos(despachos)
                messages.success(request, f"Despacho {despacho['codigo']} actualizado correctamente.")
                return redirect('despachos')
        except ValueError:
            messages.error(request, "El peso y la capacidad deben ser valores numéricos válidos.")

    estados_disponibles = ['En Preparación', 'En Tránsito', 'Incidencia', 'Entregado']
    return render(request, 'logistica/editar.html', {
        'despacho': despacho,
        'estados_disponibles': estados_disponibles
    })

def eliminar_despacho(request, id):
    despachos = _obtener_despachos()
    despacho = next((d for d in despachos if d['id'] == id), None)
    if despacho:
        despachos = [d for d in despachos if d['id'] != id]
        _guardar_despachos(despachos)
        messages.success(request, f"Despacho {despacho['codigo']} eliminado correctamente.")
    else:
        messages.error(request, "El despacho no existe.")
    return redirect('despachos')