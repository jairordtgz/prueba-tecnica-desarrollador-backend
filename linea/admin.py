from django.contrib import admin

from .models import LineaServicio


@admin.register(LineaServicio)
class LineaServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'linea_numero', 'estado_linea', 'saldo_vencido', 'is_active')
    list_filter = ('estado_linea', 'is_active')
    search_fields = ('cliente__identificacion', 'cliente__razon_social')