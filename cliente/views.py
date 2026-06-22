from rest_framework import viewsets
from core.permissions import SoloAdminPuedeEliminar
from .filters import FiltroCliente
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filterset_class = FiltroCliente
    permission_classes = [SoloAdminPuedeEliminar]

    def perform_destroy(self, instance):
        # Eliminación lógica
        instance.is_active = False
        instance.save(update_fields=['is_active'])