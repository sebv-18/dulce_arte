import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from productos.models import Ingrediente
from pedidos.models import Cliente, Pedido, DetallePedido, Cotizacion
from despachos.models import Despacho
from inventario.models import MovimientoInventario


def seed():
    print("Creando usuario administrador...")
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@dulcearte.cl', 'admin123')
        print("Superusuario 'admin' creado con contraseña 'admin123'")
    else:
        print("Superusuario 'admin' ya existe.")

    print("Poblando ingredientes de alta pastelería (BOM)...")
    ingredientes_data = [
        {"nombre": "Harina de Almendras Finas California", "unidad_medida": "Kg", "stock_actual": Decimal("18.5"), "stock_minimo": Decimal("10.0")},
        {"nombre": "Chocolate Belga Callebaut 70% Cacao", "unidad_medida": "Kg", "stock_actual": Decimal("24.0"), "stock_minimo": Decimal("15.0")},
        {"nombre": "Mantequilla Francesa Elle & Vire AOP", "unidad_medida": "Kg", "stock_actual": Decimal("4.2"), "stock_minimo": Decimal("12.0")},  # Alerta bajo stock
        {"nombre": "Vainas de Vainilla Bourbon de Madagascar", "unidad_medida": "Unidades", "stock_actual": Decimal("15.0"), "stock_minimo": Decimal("30.0")},  # Crítico
        {"nombre": "Pistacho Puro Bronte DOP Sicilia (Pasta)", "unidad_medida": "Kg", "stock_actual": Decimal("2.1"), "stock_minimo": Decimal("5.0")},  # Crítico
        {"nombre": "Frambuesas Frescas Selección Maule", "unidad_medida": "Kg", "stock_actual": Decimal("14.0"), "stock_minimo": Decimal("8.0")},
        {"nombre": "Azúcar Glass Impalpable Seda", "unidad_medida": "Kg", "stock_actual": Decimal("45.0"), "stock_minimo": Decimal("20.0")},
        {"nombre": "Láminas de Oro Comestible 24K", "unidad_medida": "Láminas", "stock_actual": Decimal("8.0"), "stock_minimo": Decimal("20.0")},  # Crítico
        {"nombre": "Flores Orgánicas Comestibles de Invernadero", "unidad_medida": "Cajas", "stock_actual": Decimal("6.0"), "stock_minimo": Decimal("10.0")},
        {"nombre": "Crema de Leche Fresca 36% Materia Grasa", "unidad_medida": "Litros", "stock_actual": Decimal("35.0"), "stock_minimo": Decimal("15.0")},
    ]

    ing_objs = {}
    for item in ingredientes_data:
        obj, created = Ingrediente.objects.update_or_create(
            nombre=item["nombre"],
            defaults={
                "unidad_medida": item["unidad_medida"],
                "stock_actual": item["stock_actual"],
                "stock_minimo": item["stock_minimo"],
                "activo": True
            }
        )
        ing_objs[item["nombre"]] = obj

    print("Poblando clientes...")
    clientes_data = [
        {"nombre": "Camila Soto Lyon", "telefono": "+56 9 8452 1190", "correo": "camila.soto@email.com"},
        {"nombre": "Valentina Rossi", "telefono": "+56 9 9123 4455", "correo": "valentina.rossi@email.com"},
        {"nombre": "Matías Larraín Errázuriz", "telefono": "+56 9 7334 8812", "correo": "matias.larrain@email.com"},
        {"nombre": "Sofía Echeverría", "telefono": "+56 9 6554 9921", "correo": "sofia.echeverria@email.com"},
        {"nombre": "Gonzalo Morales", "telefono": "+56 9 5214 7780", "correo": "gonzalo.morales@email.com"},
    ]

    cli_objs = []
    for c in clientes_data:
        obj, _ = Cliente.objects.update_or_create(
            correo=c["correo"],
            defaults={"nombre": c["nombre"], "telefono": c["telefono"]}
        )
        cli_objs.append(obj)

    print("Poblando pedidos con etapas de Kanban...")
    now = timezone.now()
    pedidos_data = [
        {
            "id": 8842,
            "cliente": cli_objs[0],
            "descripcion": "Torta Nupcial Botánica 3 Pisos - Bizcocho Vainilla Bourbon con ganache de frutos rojos y flores comestibles prensadas.",
            "diseno": "Paleta ivory con toques de rosa cuarzo y pan de oro 24k en bordes desgastados.",
            "fecha_entrega": now + timedelta(days=2, hours=4),
            "precio_total": Decimal("185000.00"),
            "estado": "RECIBIDO"
        },
        {
            "id": 5519,
            "cliente": cli_objs[1],
            "descripcion": "Tarta Saint-Honoré Caramelo & Fleur de Sel - Base hojaldre invertido con profiteroles caramelizados y chantilly diplomata.",
            "diseno": "Acabado clásico francés con caramelo crocante brillante.",
            "fecha_entrega": now + timedelta(hours=6),
            "precio_total": Decimal("48000.00"),
            "estado": "PREPARACION"
        },
        {
            "id": 6320,
            "cliente": cli_objs[2],
            "descripcion": "Colección Box Éclair Gourmet (12 uds) & Torre Macarons Pistacho Bronte.",
            "diseno": "Empaque de lujo rígido con lazo de terciopelo café chocolate y sello lacrado.",
            "fecha_entrega": now + timedelta(hours=3),
            "precio_total": Decimal("62500.00"),
            "estado": "HORNEADO"
        },
        {
            "id": 9104,
            "cliente": cli_objs[3],
            "descripcion": "Torta Ópera Imperial Chocolate Belga - Bizcocho Gioconda, almíbar de café arábica y ganache Valrhona 70%.",
            "diseno": "Glaseado espejo chocolate brillante con caligrafía dorada de aniversario.",
            "fecha_entrega": now + timedelta(hours=2),
            "precio_total": Decimal("75000.00"),
            "estado": "CALIDAD"
        },
        {
            "id": 4281,
            "cliente": cli_objs[4],
            "descripcion": "Pavlova Real Frutos del Bosque - Merengue suizo crujiente por fuera y marshmallow por dentro, crema mascarpone.",
            "diseno": "Corona exuberante de frambuesas de Maule, moras silvestres y menta fresca.",
            "fecha_entrega": now + timedelta(hours=1),
            "precio_total": Decimal("52000.00"),
            "estado": "LISTO"
        },
    ]

    ped_objs = []
    for p in pedidos_data:
        obj, _ = Pedido.objects.update_or_create(
            id=p["id"],
            defaults={
                "cliente": p["cliente"],
                "descripcion": p["descripcion"],
                "diseno": p["diseno"],
                "fecha_entrega": p["fecha_entrega"],
                "precio_total": p["precio_total"],
                "estado": p["estado"],
            }
        )
        ped_objs.append(obj)

    print("Poblando despachos...")
    despachos_data = [
        {
            "pedido": ped_objs[4],  # LISTO
            "direccion": "Av. Santa María 5800, Dpto 1402, Vitacura",
            "ruta": "Zona Oriente - Despacho Climatizado #1",
            "estado": "EN_RUTA",
            "firma_receptor": "",
            "fecha_entrega": now + timedelta(minutes=45)
        },
        {
            "pedido": ped_objs[3],  # CALIDAD
            "direccion": "Av. Las Condes 12400, Casa 8, Lo Barnechea",
            "ruta": "Zona Cordillera - Despacho Climatizado #2",
            "estado": "PENDIENTE",
            "firma_receptor": "",
            "fecha_entrega": now + timedelta(hours=2)
        },
        {
            "pedido": ped_objs[2],  # HORNEADO
            "direccion": "Av. Providencia 1920, Oficina 501, Providencia",
            "ruta": "Zona Centro-Providencia",
            "estado": "PENDIENTE",
            "firma_receptor": "",
            "fecha_entrega": now + timedelta(hours=3)
        },
    ]

    for d in despachos_data:
        Despacho.objects.update_or_create(
            pedido=d["pedido"],
            defaults={
                "direccion": d["direccion"],
                "ruta": d["ruta"],
                "estado": d["estado"],
                "firma_receptor": d["firma_receptor"],
                "fecha_entrega": d["fecha_entrega"]
            }
        )

    print("¡Datos mock sembrados con éxito en la base de datos!")


if __name__ == '__main__':
    seed()
