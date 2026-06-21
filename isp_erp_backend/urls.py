from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cliente.views import ClienteViewSet
from linea.views import LineaServicioViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'lineas', LineaServicioViewSet, basename='linea')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]