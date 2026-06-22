from rest_framework import viewsets
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import FiltroLineaServicio
from .models import LineaServicio
from .serializers import LineaServicioSerializer

from cobranza.models import Rubro
from cobranza.serializers import CollectionsRequestLogSerializer
from core.permissions import SoloAdminPuedeEliminar

class LineaServicioViewSet(viewsets.ModelViewSet):
    queryset = LineaServicio.objects.select_related('cliente').all()
    serializer_class = LineaServicioSerializer
    filterset_class = FiltroLineaServicio
    permission_classes = [SoloAdminPuedeEliminar]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])

    @action(detail=True, methods=['get'], url_path='estado-cobranza')
    def estado_cobranza(self, request, pk=None):
        linea = self.get_object()

        unpaid_count = Rubro.objects.filter(
            linea_servicio=linea,
            estado_rubro=Rubro.EstadoRubro.NO_PAGADO,
            fecha_vencimiento__lt=timezone.now(),
        ).count()

        ultimos_logs = linea.logs_cobranza.all()[:5]

        return Response({
            'linea_id': linea.id,
            'estado_linea': linea.estado_linea,
            'saldo_vencido': linea.saldo_vencido,
            'unpaid_count': unpaid_count,
            'ultimos_logs': CollectionsRequestLogSerializer(ultimos_logs, many=True).data,
        }) 