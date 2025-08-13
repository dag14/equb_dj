from rest_framework import viewsets, permissions
from equb.models import PayoutSchedule
from equb.serializers.payout_schedule_serializer import PayoutScheduleSerializer
from django_filters.rest_framework import DjangoFilterBackend

class PayoutScheduleViewSet(viewsets.ModelViewSet):
    queryset = PayoutSchedule.objects.all()
    serializer_class = PayoutScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]  # to be tightened later
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["group", "recipient", "status", "scheduled_date"]
