from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import LineaServicio


class LineaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineaServicio
        fields = [
            'id', 'cliente', 'linea_numero', 'estado_linea',
            'fecha_instalacion', 'saldo_vencido', 'is_active',
            'created_at', 'modified_at',
        ]
        read_only_fields = ['id', 'saldo_vencido', 'created_at', 'modified_at']
        validators = [
            UniqueTogetherValidator(
                queryset=LineaServicio.objects.all(),
                fields=['cliente', 'linea_numero'],
                message='Este cliente ya tiene una línea con ese número.',
            )
        ]

    def validate(self, attrs):
        estado = attrs.get('estado_linea', getattr(self.instance, 'estado_linea', None))
        cliente = attrs.get('cliente', getattr(self.instance, 'cliente', None))

        if estado == LineaServicio.EstadoLinea.ACTIVO and cliente and not cliente.is_active:
            raise serializers.ValidationError(
                {'estado_linea': 'No se puede activar una línea de un cliente inactivo.'}
            )
        return attrs