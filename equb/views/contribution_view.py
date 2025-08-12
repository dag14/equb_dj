from rest_framework import viewsets, permissions
from equb.models import Contribution
from equb.serializers.contribution_serializer import ContributionSerializer

class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]  # For now, require login
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["member", "group", "status", "date"]    

    def perform_create(self, serializer):
        # Set recorded_by automatically from request.user
        serializer.save(recorded_by=self.request.user)
