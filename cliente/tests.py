import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status
from rest_framework.test import APIClient

from .models import Cliente


@pytest.mark.django_db
class TestClienteModel:
    def test_identificacion_unica(self):
        Cliente.objects.create(identificacion='0999999999', razon_social='Cliente A')
        with pytest.raises(IntegrityError):
            Cliente.objects.create(identificacion='0999999999', razon_social='Cliente B')


@pytest.mark.django_db
class TestClienteEndpoint:
    def setup_method(self):
        self.client = APIClient()
        self.user_normal = User.objects.create_user(username='user1', password='pass123')
        self.user_admin = User.objects.create_user(
            username='admin1', password='pass123', is_staff=True,
        )

    def test_crear_cliente_autenticado(self):
        self.client.force_authenticate(user=self.user_normal)
        response = self.client.post('/api/clientes/', {
            'identificacion': '0911111111',
            'razon_social': 'Cliente Test',
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_no_autenticado_rechazado(self):
        response = self.client.get('/api/clientes/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_requiere_admin(self):
        cliente = Cliente.objects.create(identificacion='0922222222', razon_social='Cliente X')
        self.client.force_authenticate(user=self.user_normal)
        response = self.client.delete(f'/api/clientes/{cliente.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_admin_hace_soft_delete(self):
        cliente = Cliente.objects.create(identificacion='0933333333', razon_social='Cliente Y')
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.delete(f'/api/clientes/{cliente.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        cliente.refresh_from_db()
        assert cliente.is_active is False
