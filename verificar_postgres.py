import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client as HttpClient
from django.contrib.auth.models import User
from pedidos.models import Cliente, Pedido
from productos.models import Ingrediente
from despachos.models import Despacho
from inventario.models import MovimientoInventario


def run_checks():
    print("=" * 70)
    print("INICIANDO COMPROBACIONES OBLIGATORIAS EN POSTGRESQL REAL")
    print("=" * 70)

    client = HttpClient()

    # 1. Comprobación de registro
    print("\n[CHECK 1/8] Comprobando Registro de Usuario y Cliente en PostgreSQL...")
    username = "camilatest_pg"
    email = "camilatest@email.com"

    # Limpiar si existía de prueba previa
    User.objects.filter(username=username).delete()
    Cliente.objects.filter(correo=email).delete()

    reg_payload = {
        "nombre": "Camila Soto Test",
        "username": username,
        "correo": email,
        "telefono": "+56 9 8452 9999",
        "password1": "DulceArte2026!",
        "password2": "DulceArte2026!"
    }

    res_reg = client.post("/registro/", data=json.dumps(reg_payload), content_type="application/json")
    assert res_reg.status_code == 200, f"Error en registro: {res_reg.content}"
    assert res_reg.json().get("success"), "El registro no devolvió success=True"

    # Verificar en PostgreSQL
    user_db = User.objects.filter(username=username).first()
    assert user_db is not None, "El usuario Django no se encontró en PostgreSQL"
    assert user_db.check_password("DulceArte2026!"), "La contraseña no fue encriptada correctamente"

    cliente_db = Cliente.objects.filter(usuario=user_db).first()
    assert cliente_db is not None, "El modelo Cliente no se creó en PostgreSQL"
    assert cliente_db.nombre == "Camila Soto Test", "El nombre del cliente no coincide"
    assert cliente_db.telefono == "+56 9 8452 9999", "El teléfono no coincide"
    assert cliente_db.correo == email, "El correo no coincide"
    print(" -> ÉXITO: Usuario Django y Cliente PostgreSQL creados y vinculados correctamente.")

    # 2. Comprobación de inicio de sesión
    print("\n[CHECK 2/8] Comprobando Inicio de Sesión...")
    client.logout()  # Cerrar la sesión del registro previo para probar login desde cero

    # Credenciales incorrectas
    res_bad = client.post("/login/", data=json.dumps({"username": username, "password": "PasswordInvalida"}), content_type="application/json")
    assert res_bad.status_code == 400, "El login no rechazó la contraseña incorrecta"
    assert "error" in res_bad.json(), "No devolvió mensaje de error"

    # Credenciales correctas
    res_ok = client.post("/login/", data=json.dumps({"username": username, "password": "DulceArte2026!"}), content_type="application/json")
    assert res_ok.status_code == 200, f"Error en login: {res_ok.content}"
    assert res_ok.json().get("success"), "El login no fue exitoso"
    assert res_ok.json().get("is_staff") is False, "El cliente no debería ser staff"
    assert res_ok.json().get("redirect") == "/", "El cliente no fue redirigido a la vista de cliente"
    print(" -> ÉXITO: Login funcional con manejo de sesiones y validación de credenciales.")

    # 3. Comprobación de seguridad: Cliente NO puede acceder al panel administrativo
    print("\n[CHECK 3/8] Comprobando que Cliente NO pueda ingresar al Panel de Administración...")
    res_panel_cliente = client.get("/panel/")
    assert res_panel_cliente.status_code == 403, f"Seguridad fallida: cliente obtuvo código {res_panel_cliente.status_code} en vez de 403"
    print(" -> ÉXITO: Cliente bloqueado del panel administrativo (HTTP 403 Forbidden).")

    # 4. Comprobación de acceso: Administrador SÍ puede acceder al panel
    print("\n[CHECK 4/8] Comprobando que Administrador SÍ pueda ingresar a su Panel...")
    admin_client = HttpClient()
    # Asegurar admin existente
    admin_user = User.objects.filter(username="admin").first()
    if not admin_user:
        admin_user = User.objects.create_superuser("admin", "admin@dulcearte.cl", "admin123")
    else:
        admin_user.set_password("admin123")
        admin_user.save()

    res_admin_login = admin_client.post("/login/", data=json.dumps({"username": "admin", "password": "admin123"}), content_type="application/json")
    assert res_admin_login.status_code == 200, "Error en login de administrador"
    assert res_admin_login.json().get("is_staff") is True, "El admin debe tener is_staff=True"
    assert res_admin_login.json().get("redirect") == "/panel/", "El admin debe ser redirigido a /panel/"

    res_panel_admin = admin_client.get("/panel/")
    assert res_panel_admin.status_code == 200, f"Admin no pudo acceder al panel: {res_panel_admin.status_code}"
    print(" -> ÉXITO: Administrador ingresa correctamente a su Panel Taller (HTTP 200 OK).")

    # 5. Comprobación de persistencia: Creación de pedido desde el cliente
    print("\n[CHECK 5/8] Comprobando Persistencia de Pedido en PostgreSQL...")
    pedido_payload = {
        "descripcion": "Torta Nupcial Especial de Prueba 25 Porciones",
        "diseno": "Glaseado rosa y hojas de menta fresca",
        "fecha_entrega": "2026-11-20T16:00:00Z",
        "precio_total": 72000.0,
        "estado": "RECIBIDO"
    }

    res_order = client.post("/api/pedidos/", data=json.dumps(pedido_payload), content_type="application/json")
    assert res_order.status_code == 201, f"Error al crear pedido: {res_order.content}"
    nuevo_pedido_id = res_order.json()["id"]

    # Verificar en PostgreSQL
    pedido_db = Pedido.objects.filter(id=nuevo_pedido_id).first()
    assert pedido_db is not None, "El pedido no se guardó en PostgreSQL"
    assert pedido_db.cliente == cliente_db, "El pedido no quedó asociado al cliente autenticado"
    assert pedido_db.precio_total == 72000.0, "El precio no coincide"
    print(f" -> ÉXITO: Pedido #{nuevo_pedido_id} creado y persistido en PostgreSQL vinculado al cliente.")

    # 6. Comprobación de cambio de estado en Kanban
    print("\n[CHECK 6/8] Comprobando Persistencia de Cambio de Estado (Kanban)...")
    res_status = admin_client.post(
        f"/api/pedidos/{nuevo_pedido_id}/cambiar_estado/",
        data=json.dumps({"estado": "HORNEADO"}),
        content_type="application/json"
    )
    assert res_status.status_code == 200, f"Error al cambiar estado: {res_status.content}"

    pedido_db.refresh_from_db()
    assert pedido_db.estado == "HORNEADO", "El nuevo estado no persistió en PostgreSQL"
    print(f" -> ÉXITO: Estado del pedido #{nuevo_pedido_id} actualizado a HORNEADO en PostgreSQL.")

    # 7. Comprobación de Reabastecimiento de Inventario
    print("\n[CHECK 7/8] Comprobando Persistencia de Inventario y Movimientos...")
    ingrediente = Ingrediente.objects.first()
    assert ingrediente is not None, "No hay ingredientes en base de datos"
    stock_anterior = ingrediente.stock_actual

    res_restock = admin_client.post(
        f"/api/ingredientes/{ingrediente.id}/reabastecer/",
        data=json.dumps({"cantidad": 3.0, "motivo": "Comprobación automática"}),
        content_type="application/json"
    )
    assert res_restock.status_code == 200, f"Error en reabastecimiento: {res_restock.content}"

    ingrediente.refresh_from_db()
    assert ingrediente.stock_actual == stock_anterior + 3, "El stock no incrementó en PostgreSQL"

    mov = MovimientoInventario.objects.filter(ingrediente=ingrediente, motivo__contains="Comprobación automática").first()
    assert mov is not None, "No se registró el MovimientoInventario en PostgreSQL"
    assert mov.tipo == "ENTRADA", "El tipo de movimiento no es ENTRADA"
    print(f" -> ÉXITO: Stock de {ingrediente.nombre} actualizado (+3) y MovimientoInventario registrado en PostgreSQL.")

    # 8. Comprobación de Rastreo de Pedido y Cierre de Sesión
    print("\n[CHECK 8/8] Comprobando Rastreador de Pedido y Logout con CSRF/POST...")
    res_rastreo = client.get(f"/api/pedidos/rastreo/?codigo=DA-2026-{nuevo_pedido_id}")
    assert res_rastreo.status_code == 200, "Error en endpoint de rastreo"
    assert res_rastreo.json()["estado"] == "HORNEADO", "El rastreador no devolvió el estado actualizado desde PostgreSQL"

    res_logout = client.post("/logout/", content_type="application/json")
    assert res_logout.status_code == 200, "Error en logout"
    res_me = client.get("/api/auth/me/")
    assert res_me.json()["isLoggedIn"] is False, "La sesión aún sigue activa tras logout"
    print(" -> ÉXITO: Rastreador devuelve estado real desde PostgreSQL y logout finaliza la sesión.")

    # Limpieza final de datos de prueba
    pedido_db.delete()
    cliente_db.delete()
    user_db.delete()
    mov.delete()
    ingrediente.stock_actual = stock_anterior
    ingrediente.save()

    print("\n" + "=" * 70)
    print("¡TODAS LAS COMPROBACIONES OBLIGATORIAS PASARON CON ÉXITO (100%)!")
    print("=" * 70)


if __name__ == "__main__":
    run_checks()
