from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Despacho
from .serializers import DespachoSerializer


class DespachoViewSet(viewsets.ModelViewSet):
    queryset = Despacho.objects.select_related('pedido', 'pedido__cliente').all().order_by('-id')
    serializer_class = DespachoSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Despacho.objects.none()
        if user.is_staff:
            return Despacho.objects.select_related('pedido', 'pedido__cliente').all().order_by('-id')
        if hasattr(user, 'cliente'):
            return Despacho.objects.filter(pedido__cliente=user.cliente).select_related('pedido', 'pedido__cliente').order_by('-id')
        return Despacho.objects.none()

    def get_permissions(self):
        if self.action in ['firmar_entrega', 'create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def firmar_entrega(self, request, pk=None):
        despacho = self.get_object()
        receptor = request.data.get('receptor', 'Recepción Conforme').strip()
        comprobante = request.data.get('comprobante', '')

        despacho.estado = 'ENTREGADO'
        despacho.firma_receptor = receptor or 'Recepción Conforme'
        if comprobante:
            despacho.comprobante_url = comprobante
        despacho.fecha_entrega = timezone.now()
        despacho.save()

        # Asegurar que el pedido correspondiente quede marcado como LISTO
        pedido = despacho.pedido
        if pedido.estado != 'LISTO':
            pedido.estado = 'LISTO'
            pedido.save()

        return Response({
            "success": True,
            "despacho_id": despacho.id,
            "pedido_id": pedido.id,
            "estado": despacho.estado,
            "firma_receptor": despacho.firma_receptor,
            "fecha_entrega": despacho.fecha_entrega.isoformat(),
            "mensaje": f"Despacho del pedido #{pedido.id} entregado y firmado con éxito."
        })
