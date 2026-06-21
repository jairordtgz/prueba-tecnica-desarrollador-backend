from rest_framework import viewsets

from .filters import FiltroLineaServicio
from .models import LineaServicio
from .serializers import LineaServicioSerializer


class LineaServicioViewSet(viewsets.ModelViewSet):
    queryset = LineaServicio.objects.select_related('cliente').all()
    serializer_class = LineaServicioSerializer
    filterset_class = FiltroLineaServicio

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])     