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

def _obtener_usuarios():
    ruta = os.path.join(settings.BASE_DIR, 'data', 'usuarios.json')
    if not os.path.exists(ruta):
        return []
    with open(ruta, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)

def _guardar_usuarios(lista_usuarios):
    ruta = os.path.join(settings.BASE_DIR, 'data', 'usuarios.json')
    with open(ruta, 'w', encoding='utf-8') as archivo:
        json.dump(lista_usuarios, archivo, indent=2, ensure_ascii=False)

def landing(request):
    """One Page de bienvenida"""
    return render(request, 'logistica/landing.html')

def login_view(request):
    """Login de Administrador (Simulado, sin base de datos)"""
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '').strip()
        if not usuario:
            usuario = "Administrador"

        messages.success(request, f"¡Sesión iniciada con éxito! Bienvenido Administrador {usuario}.")
        return redirect('index')

    return render(request, 'logistica/login.html')

def registro_view(request):
    """Registro de nuevos Administradores (Persistencia en JSON, sin Models)"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        usuario = request.POST.get('usuario', '').strip()
        email = request.POST.get('email', '').strip()
        cargo = request.POST.get('cargo', '').strip()
        password = request.POST.get('password', '').strip()

        if not all([nombre, usuario, email, cargo, password]):
            messages.error(request, "Todos los campos del registro son obligatorios.")
        else:
            usuarios = _obtener_usuarios()
            # Guardamos el nuevo administrador
            nuevo_usuario = {
                "id": len(usuarios) + 1,
                "nombre": nombre,
                "usuario": usuario,
                "email": email,
                "cargo": cargo,
                "rol": "Administrador"
            }
            usuarios.append(nuevo_usuario)
            _guardar_usuarios(usuarios)

            messages.success(request, f"¡Administrador '{usuario}' registrado exitosamente! Ahora puedes iniciar sesión.")
            return redirect('login')

    return render(request, 'logistica/registro.html')

def cliente_tracking(request):
    """Portal de consulta para Clientes mediante Código de Envío"""
    codigo_buscado = request.GET.get('codigo', '').strip()
    despacho_encontrado = None
    busqueda_realizada = False

    if codigo_buscado:
        busqueda_realizada = True
        despachos = _obtener_despachos()
        for d in despachos:
            if d['codigo'].upper() == codigo_buscado.upper():
                despacho_encontrado = d
                break

    return render(request, 'logistica/cliente.html', {
        'codigo_buscado': codigo_buscado,
        'despacho': despacho_encontrado,
        'busqueda_realizada': busqueda_realizada
    })

def index(request):
    """Dashboard de Administrador"""
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
    """Listado del Administrador con gestión"""
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
                    messages.warning(request, f"¡Alerta de Cubicaje! La carga ({val_peso} kg) supera la capacidad ({val_capacidad} kg).")
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
                        "carga": ["Lote de instrumentos registrado"]
                    }
                    despachos.append(nuevo_registro)
                    _guardar_despachos(despachos)
                    messages.success(request, f"Despacho {codigo} registrado exitosamente.")
                    return redirect('despachos')
            except ValueError:
                messages.error(request, "Valores numéricos inválidos.")

    return render(request, 'logistica/nuevo.html')

def editar_despacho(request, id):
    despachos = _obtener_despachos()
    despacho = next((d for d in despachos if d['id'] == id), None)
    
    if not despacho:
        messages.error(request, "El despacho no existe.")
        return redirect('despachos')

    if request.method == 'POST':
        try:
            val_peso = float(request.POST.get('peso', 0))
            val_capacidad = float(request.POST.get('capacidad', 0))

            if val_peso > val_capacidad:
                messages.warning(request, f"¡Alerta! La carga supera la capacidad.")
            else:
                despacho['destino'] = request.POST.get('destino', '').strip()
                despacho['conductor'] = request.POST.get('conductor', '').strip()
                despacho['patente'] = request.POST.get('patente', '').strip()
                despacho['peso_kg'] = val_peso
                despacho['capacidad_kg'] = val_capacidad
                despacho['estado'] = request.POST.get('estado', '').strip()
                despacho['eta'] = request.POST.get('eta', '').strip()

                _guardar_despachos(despachos)
                messages.success(request, f"Despacho {despacho['codigo']} modificado exitosamente.")
                return redirect('despachos')
        except ValueError:
            messages.error(request, "Valores numéricos inválidos.")

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
        messages.success(request, f"Despacho {despacho['codigo']} eliminado.")
    return redirect('despachos')