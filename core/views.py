from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from cliente.models import Cliente
from cobranza.models import Rubro
from linea.models import LineaServicio


@api_view(['GET'])
@permission_classes([AllowAny])
def healthcheck(request):
    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 503
    return Response(
        {'status': 'ok' if db_ok else 'degraded', 'database': db_ok},
        status=status_code,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def metricas_basicas(request):
    return Response({
        'clientes_activos': Cliente.objects.filter(is_active=True).count(),
        'lineas_activas': LineaServicio.objects.filter(is_active=True).count(),
        'lineas_suspendidas': LineaServicio.objects.filter(estado_linea='SUSPENDIDO').count(),
        'rubros_no_pagados': Rubro.objects.filter(estado_rubro='NO_PAGADO').count(),
    })