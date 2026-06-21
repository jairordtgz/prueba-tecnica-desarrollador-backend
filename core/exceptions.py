from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

def excepcion_personalizada(exc, contexto): 
    response = exception_handler(exc, contexto)
    
    if response is not None: 
        return response
    
    if isinstance(exc, contexto): 
        return Response(
            {'detail': 'Conflicto en los datos'},
            status=status.HTTP_409_CONFLICT
            
        )
    
    return None
