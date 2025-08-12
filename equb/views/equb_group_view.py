from rest_framework import viewsets, permissions
from equb.models import EqubGroup
from equb.serializers.equb_group_serializer import EqubGroupSerializer
from django_filters.rest_framework import DjangoFilterBackend

class EqubGroupViewSet(viewsets.ModelViewSet):
    queryset = EqubGroup.objects.all()
    serializer_class = EqubGroupSerializer
    permission_classes = [permissions.AllowAny] # I'll later tighten permissions
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "admin"]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

