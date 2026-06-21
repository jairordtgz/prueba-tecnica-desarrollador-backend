import django_filters

from .models import LineaServicio


class FiltroLineaServicio(django_filters.FilterSet):
    cliente_id = django_filters.NumberFilter(field_name='cliente_id')

    class Meta:
        model = LineaServicio
        fields = ['estado_linea', 'is_active']