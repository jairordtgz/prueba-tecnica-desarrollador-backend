from rest_framework import serializers

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id', 'identificacion', 'razon_social', 'email', 'celular',
            'is_active', 'created_at', 'modified_at',
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']

    def validar_identificacion(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('La identificación no puede estar vacía.')
        return value