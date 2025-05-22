from rest_framework import viewsets, permissions
from applications.rent.models import Rent
from applications.rent.permissions import IsOwnerOrStaff
from applications.rent.serializers import RentSerializer


class RentViewSet(viewsets.ModelViewSet):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Rent.objects.all()
        return Rent.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

