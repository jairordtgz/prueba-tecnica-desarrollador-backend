from rest_framework.permissions import BasePermission


class SoloAdminPuedeEliminar(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'DELETE':
            return request.user.is_staff
        return True