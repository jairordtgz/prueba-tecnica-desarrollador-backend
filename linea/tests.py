import pytest
from django.db import IntegrityError

from cliente.models import Cliente

from .models import LineaServicio
from .serializers import LineaServicioSerializer


@pytest.mark.django_db
class TestLineaServicioModel:
    def test_unique_linea_por_cliente(self):
        cliente = Cliente.objects.create(identificacion='0944444444', razon_social='Cliente Linea')
        LineaServicio.objects.create(cliente=cliente, linea_numero=1)
        with pytest.raises(IntegrityError):
            LineaServicio.objects.create(cliente=cliente, linea_numero=1)

    def test_no_activar_si_cliente_inactivo(self):
        cliente = Cliente.objects.create(
            identificacion='0955555555', razon_social='Cliente Inactivo', is_active=False,
        )
        serializer = LineaServicioSerializer(data={
            'cliente': cliente.id, 'linea_numero': 1, 'estado_linea': 'ACTIVO',
        })
        assert not serializer.is_valid()
        assert 'estado_linea' in serializer.errors