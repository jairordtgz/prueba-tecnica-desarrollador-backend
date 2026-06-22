from rest_framework import serializers

from .models import CollectionsRequestLog


class CollectionsRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionsRequestLog
        fields = [
            'id', 'started_at', 'finished_at', 'status',
            'unpaid_count', 'action_taken', 'error_message',
        ]