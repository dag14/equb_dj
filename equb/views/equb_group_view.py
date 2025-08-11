from rest_framework import viewsets, permissions
from equb.models import EqubGroup
from equb.serializers.equb_group_serializer import EqubGroupSerializer

class EqubGroupViewSet(viewsets.ModelViewSet):
    queryset = EqubGroup.objects.all()
    serializer_class = EqubGroupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
