from django.db import models
from core.models import Auditoria

class Cliente(Auditoria): 
    identificacion = models.CharField(max_length=13, unique=True, db_index=True)
    razon_social = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.identificacion} - {self.razon_social}'