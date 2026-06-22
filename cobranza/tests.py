import pytest
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from cliente.models import Cliente
from linea.models import LineaServicio

from .models import CollectionsRequestLog, Rubro
from .services import MorosidadService
from .tasks import procesar_morosidad


@pytest.fixture
def linea_activa(db):
    cliente = Cliente.objects.create(identificacion='0966666666', razon_social='Cliente Cobranza')
    return LineaServicio.objects.create(cliente=cliente, linea_numero=1, estado_linea='ACTIVO')


@pytest.mark.django_db
class TestMorosidadService:
    def test_suspende_si_hay_rubros_vencidos(self, linea_activa):
        Rubro.objects.create(
            linea_servicio=linea_activa, valor_total=Decimal('30.00'),
            estado_rubro='NO_PAGADO',
            fecha_emision=timezone.now() - timedelta(days=40),
            fecha_vencimiento=timezone.now() - timedelta(days=10),
        )
        resultado = MorosidadService().procesar_linea(linea_activa)
        linea_activa.refresh_from_db()

        assert resultado.unpaid_count == 1
        assert linea_activa.estado_linea == 'SUSPENDIDO'
        assert linea_activa.saldo_vencido == Decimal('30.00')
        assert resultado.action_taken == 'SUSPEND'

    def test_reactiva_si_ya_no_hay_rubros_vencidos(self, linea_activa):
        linea_activa.estado_linea = 'SUSPENDIDO'
        linea_activa.save()

        resultado = MorosidadService().procesar_linea(linea_activa)
        linea_activa.refresh_from_db()

        assert linea_activa.estado_linea == 'ACTIVO'
        assert resultado.action_taken == 'UNSUSPEND'

    def test_no_suspende_no_instalado(self, linea_activa):
        linea_activa.estado_linea = 'NO_INSTALADO'
        linea_activa.save()
        Rubro.objects.create(
            linea_servicio=linea_activa, valor_total=Decimal('20.00'),
            estado_rubro='NO_PAGADO',
            fecha_emision=timezone.now() - timedelta(days=40),
            fecha_vencimiento=timezone.now() - timedelta(days=10),
        )
        resultado = MorosidadService().procesar_linea(linea_activa)
        linea_activa.refresh_from_db()

        assert linea_activa.estado_linea == 'NO_INSTALADO'
        assert resultado.action_taken == 'NONE'
        assert linea_activa.saldo_vencido == Decimal('20.00')


@pytest.mark.django_db
class TestProcesarMorosidadTask:
    def test_crea_log_por_linea_activa(self, linea_activa):
        procesar_morosidad()
        assert CollectionsRequestLog.objects.filter(linea_servicio=linea_activa).count() == 1

    def test_idempotente_en_doble_ejecucion(self, linea_activa):
        Rubro.objects.create(
            linea_servicio=linea_activa, valor_total=Decimal('15.00'),
            estado_rubro='NO_PAGADO',
            fecha_emision=timezone.now() - timedelta(days=40),
            fecha_vencimiento=timezone.now() - timedelta(days=10),
        )
        procesar_morosidad()
        linea_activa.refresh_from_db()
        estado_1, saldo_1 = linea_activa.estado_linea, linea_activa.saldo_vencido

        procesar_morosidad()
        linea_activa.refresh_from_db()

        assert linea_activa.estado_linea == estado_1
        assert linea_activa.saldo_vencido == saldo_1
        assert CollectionsRequestLog.objects.filter(linea_servicio=linea_activa).count() == 2