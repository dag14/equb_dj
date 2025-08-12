from rest_framework import viewsets, permissions
from equb.models import GroupMember
from equb.serializers.group_member_serializer import GroupMemberSerializer
from django_filters.rest_framework import DjangoFilterBackend

class GroupMemberViewSet(viewsets.ModelViewSet):
    queryset = GroupMember.objects.all()
    serializer_class = GroupMemberSerializer
    permission_classes = [permissions.AllowAny]  # I'll later tighten permissions
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["group", "user", "role", "status"]

    def perform_create(self, serializer):
        serializer.save()