from rest_framework import viewsets, permissions
from equb.models import Penalty
from equb.serializers.penalty_serializer import PenaltySerializer

class PenaltyViewSet(viewsets.ModelViewSet):
    queryset = Penalty.objects.all()
    serializer_class = PenaltySerializer
    permission_classes = [permissions.AllowAny]  # Will tighten later
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["group", "member", "penalty_type", "status"]

    def perform_create(self, serializer):
        serializer.save()
