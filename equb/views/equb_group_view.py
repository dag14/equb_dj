from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from equb.models import EqubGroup
from equb.serializers.equb_group_serializer import EqubGroupSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class EqubGroupViewSet(viewsets.ModelViewSet):
    serializer_class = EqubGroupSerializer
    permission_classes = [permissions.AllowAny]  # TODO: tighten later
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "admin"]
    lookup_field = "id"

    def get_queryset(self):
        return (
            EqubGroup.objects
            .annotate(total_members=Count("memberships"))
            .prefetch_related("memberships__user")   
            .select_related("admin")                
        )

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(admin=user)
    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        group = self.get_object()
        try:
            group.start()
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": group.status, "started_at": group.started_at})

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        group = self.get_object()
        try:
            group.complete()
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": group.status, "completed_at": group.completed_at})