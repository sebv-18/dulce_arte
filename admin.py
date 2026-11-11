from django.contrib import admin
from django.utils.html import format_html
from .models import Despacho


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido_link', 'cliente_nombre', 'direccion', 'ruta', 'estado_badge', 'firma_receptor', 'fecha_entrega')
    search_fields = ('pedido__id', 'pedido__cliente__nombre', 'direccion', 'ruta', 'firma_receptor')
    list_filter = ('estado', 'fecha_entrega')
    readonly_fields = ('fecha_entrega',)

    @admin.display(description="Pedido")
    def pedido_link(self, obj):
        return f"Pedido #{obj.pedido.id}"

    @admin.display(description="Cliente")
    def cliente_nombre(self, obj):
        return obj.pedido.cliente.nombre if obj.pedido and obj.pedido.cliente else "-"

    @admin.display(description="Estado de Despacho")
    def estado_badge(self, obj):
        colors = {
            'PENDIENTE': '#B45309; background-color: #FEF3C7',
            'EN_RUTA': '#1D4ED8; background-color: #DBEAFE',
            'ENTREGADO': '#047857; background-color: #D1FAE5',
        }
        style = colors.get(obj.estado, '#374151; background-color: #F3F4F6')
        return format_html(
            '<span style="color: {}; padding: 3px 10px; border-radius: 9999px; font-weight: bold; font-size: 11px;">{}</span>',
            style,
            obj.get_estado_display()
        )
