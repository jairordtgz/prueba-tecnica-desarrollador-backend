from django.db import models
from django.core.validators import MinValueValidator
from cliente.models import Cliente
from core.models import Auditoria

class LineaServicio(Auditoria): 
    
    class EstadoLinea(models.TextChoices): 
        NO_INSTALADO = 'NO_INSTALADO', 'No instalado'
        ACTIVO = 'ACTIVO', 'Activo'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
        CANCELADO = 'CANCELADO', 'Cancelado'
        
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='lineas')
    linea_numero = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    estado_linea = models.CharField(
        max_length=20, choices=EstadoLinea.choices, default=EstadoLinea.NO_INSTALADO,
    )
    fecha_instalacion = models.DateField(blank=True, null=True)
    saldo_vencido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['cliente_id', 'linea_numero']
        constraints = [
            models.UniqueConstraint(
                fields=['cliente', 'linea_numero'], name='unique_linea_por_cliente',
            )
        ]

    def __str__(self):
        return f'Línea {self.linea_numero} - {self.cliente.identificacion}'