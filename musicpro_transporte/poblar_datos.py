import os
import time
import random
import django

# 1. Configurar el entorno de Django antes de importar los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicpro_transporte.settings')
django.setup()

from faker import Faker
from django.db import transaction
from logistica.models import Conductor, Despacho, ItemCarga

fake = Faker('es_CL')


def cargar_datos_iniciales_json():
    """Carga los 4 registros base originales del caso semestral si no existen."""
    datos_base = [
        {
            "codigo": "TRP-2026-001",
            "origen": "Bodega Central Providencia",
            "destino": "Sucursal Providencia (Rock)",
            "conductor": "Carlos Valenzuela",
            "patente": "PJ-88-21",
            "peso_kg": 450.0,
            "capacidad_kg": 1200.0,
            "estado": "En Tránsito",
            "prioridad": "Alta",
            "eta": "14:30 hrs",
            "carga": [("Baterías DW", 3), ("Amplificadores Marshall", 10)]
        },
        {
            "codigo": "TRP-2026-002",
            "origen": "Bodega Central Providencia",
            "destino": "Sucursal Mall Plaza Vespucio (DJ)",
            "conductor": "Marcela Soto",
            "patente": "KLRX-44",
            "peso_kg": 180.0,
            "capacidad_kg": 800.0,
            "estado": "En Preparación",
            "prioridad": "Media",
            "eta": "17:00 hrs",
            "carga": [("Mesas Pioneer DDJ", 4), ("Audífonos Sennheiser", 20)]
        },
        {
            "codigo": "TRP-2026-003",
            "origen": "Bodega Central Providencia",
            "destino": "Franquicia Viña del Mar (Acústico)",
            "conductor": "Esteban Morales",
            "patente": "FRTY-12",
            "peso_kg": 620.0,
            "capacidad_kg": 600.0,
            "estado": "Incidencia",
            "prioridad": "Alta",
            "eta": "Retrasado",
            "carga": [("Guitarras Fender", 15), ("Teclados Yamaha", 5)]
        },
        {
            "codigo": "TRP-2026-004",
            "origen": "Bodega Central Providencia",
            "destino": "Sucursal Centro (Cumbia y Reggaetón)",
            "conductor": "Rodrigo Tapia",
            "patente": "HW-99-10",
            "peso_kg": 210.0,
            "capacidad_kg": 1000.0,
            "estado": "Entregado",
            "prioridad": "Baja",
            "eta": "11:15 hrs",
            "carga": [("Congas LP", 6), ("Micrófonos Shure", 12)]
        }
    ]

    creados = 0
    for item in datos_base:
        conductor_obj, _ = Conductor.objects.get_or_create(
            patente=item["patente"],
            defaults={
                "nombre": item["conductor"],
                "capacidad_kg": item["capacidad_kg"],
                "telefono": fake.phone_number(),
                "activo": True
            }
        )
        despacho_obj, created = Despacho.objects.get_or_create(
            codigo=item["codigo"],
            defaults={
                "origen": item["origen"],
                "destino": item["destino"],
                "conductor": conductor_obj,
                "peso_kg": item["peso_kg"],
                "estado": item["estado"],
                "prioridad": item["prioridad"],
                "eta": item["eta"],
                "observaciones": "Carga inicial migrada desde despachos.json"
            }
        )
        if created:
            creados += 1
            for desc, cant in item["carga"]:
                ItemCarga.objects.create(
                    despacho=despacho_obj,
                    descripcion=desc,
                    cantidad=cant
                )
    print(f"[OK] Se verificaron/cargaron {creados} despachos base del caso inicial.")


def asegurar_conductores_faker(minimo=30):
    """Genera conductores con Faker si hay menos del mínimo requerido."""
    actuales = list(Conductor.objects.all())
    faltantes = minimo - len(actuales)
    if faltantes > 0:
        nuevos_conductores = []
        for _ in range(faltantes):
            letras = "".join(random.choices("BCDFGHJKLMNPRSTVWXYZ", k=4))
            numeros = random.randint(10, 99)
            nuevos_conductores.append(
                Conductor(
                    nombre=fake.name(),
                    patente=f"{letras}-{numeros}",
                    capacidad_kg=random.choice([600.0, 800.0, 1000.0, 1200.0, 1500.0, 2000.0]),
                    telefono=fake.phone_number(),
                    activo=random.choice([True, True, True, False])
                )
            )
        Conductor.objects.bulk_create(nuevos_conductores)
        actuales = list(Conductor.objects.all())
    return actuales


def generar_datos_faker(cantidad_total):
    """Genera e inserta masivamente la cantidad solicitada usando Faker y bulk_create."""
    print(f"\n--- Iniciando generación de {cantidad_total:,} registros con Faker ---")
    inicio = time.time()

    conductores = asegurar_conductores_faker(50)
    ids_conductores = [c.id for c in conductores]

    # Pre-generamos catálogos con Faker para optimizar velocidad en cargas de 100k y 1M
    origenes_fake = [
        "Bodega Central Providencia",
        "Centro Distribución Pudahuel",
        "Bodega Quilicura Norte",
        "Hub Logístico San Bernardo"
    ]
    destinos_fake = [f"Sucursal {fake.city()} ({fake.street_name()})" for _ in range(100)]
    observaciones_fake = [fake.sentence(nb_words=8) for _ in range(100)]
    etas_fake = [f"{random.randint(8, 20):02d}:{random.choice(['00', '15', '30', '45'])} hrs" for _ in range(40)]
    estados = ['En Preparación', 'En Tránsito', 'Incidencia', 'Entregado']
    prioridades = ['Baja', 'Media', 'Alta']

    # Tamaño de lote óptimo para SQLite
    lote_size = 10000
    insertados = 0
    base_correlativo = Despacho.objects.count() + 1

    while insertados < cantidad_total:
        actual_batch = min(lote_size, cantidad_total - insertados)
        lote_despachos = []

        for i in range(actual_batch):
            num_codigo = base_correlativo + insertados + i
            lote_despachos.append(
                Despacho(
                    codigo=f"FAK-2026-{num_codigo:07d}",
                    origen=random.choice(origenes_fake),
                    destino=random.choice(destinos_fake),
                    conductor_id=random.choice(ids_conductores),
                    peso_kg=round(random.uniform(25.0, 1150.0), 1),
                    estado=random.choice(estados),
                    prioridad=random.choice(prioridades),
                    eta=random.choice(etas_fake),
                    observaciones=random.choice(observaciones_fake)
                )
            )

        with transaction.atomic():
            Despacho.objects.bulk_create(lote_despachos, batch_size=5000)

        insertados += actual_batch
        porcentaje = (insertados / cantidad_total) * 100
        print(f"  -> Progreso: {insertados:,} / {cantidad_total:,} ({porcentaje:.1f}%)")

    duracion = time.time() - inicio
    total_bd = Despacho.objects.count()
    print(f"\n[ÉXITO] Se insertaron {cantidad_total:,} registros en {duracion:.2f} segundos.")
    print(f"[VERIFICACIÓN] Total actual de Despachos en Base de Datos: {total_bd:,}")


def limpiar_base_datos():
    """Elimina los registros y compacta el archivo db.sqlite3 para que vuelva a pesar pocos KB."""
    from django.db import connection
    print("\nEliminando registros de la base de datos...")
    ItemCarga.objects.all().delete()
    Despacho.objects.all().delete()
    Conductor.objects.all().delete()
    print("Compactando archivo db.sqlite3 (VACUUM)...")
    with connection.cursor() as cursor:
        cursor.execute("VACUUM;")
    print("[OK] Base de datos limpia y liviana (0 registros).")


def menu():
    while True:
        print("\n" + "=" * 55)
        print("  GENERADOR DE DATOS DE PRUEBA (FAKER) - MUSICPRO")
        print("=" * 55)
        print(f"  Registros actuales -> Conductores: {Conductor.objects.count():,} | Despachos: {Despacho.objects.count():,}")
        print("-" * 55)
        print("  0. Cargar los 4 despachos originales (despachos.json)")
        print("  1. Prueba Docente: Cargar 100 datos")
        print("  2. Prueba Docente: Cargar 1.000 datos")
        print("  3. Prueba Docente: Cargar 100.000 datos")
        print("  4. Prueba Docente: Cargar 1.000.000 de datos")
        print("  5. Limpiar/Vaciar todos los datos de prueba")
        print("  6. Salir")
        print("=" * 55)

        opcion = input("Selecciona una opción (0-6): ").strip()

        if opcion == '0':
            cargar_datos_iniciales_json()
        elif opcion == '1':
            generar_datos_faker(100)
        elif opcion == '2':
            generar_datos_faker(1000)
        elif opcion == '3':
            generar_datos_faker(100000)
        elif opcion == '4':
            generar_datos_faker(1000000)
        elif opcion == '5':
            confirmar = input("¿Estás segura de borrar todos los registros? (s/n): ").strip().lower()
            if confirmar == 's':
                limpiar_base_datos()
        elif opcion == '6':
            print("Saliendo del generador...")
            break
        else:
            print("Opción no válida. Intenta nuevamente.")


if __name__ == '__main__':
    menu()