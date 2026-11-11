
from django.db import models
from pedidos.models import Pedido


class Despacho(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_RUTA', 'En ruta'),
        ('ENTREGADO', 'Entregado'),
    ]

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='despacho'
    )
    direccion = models.CharField(max_length=200)
    ruta = models.TextField(blank=True)
    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='PENDIENTE'
    )
    firma_receptor = models.CharField(max_length=120, blank=True)
    comprobante_url = models.URLField(blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Despacho del pedido #{self.pedido.id}"
