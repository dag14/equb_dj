from rest_framework import viewsets, permissions
from equb.models import PayoutSchedule
from equb.serializers.payout_schedule_serializer import PayoutScheduleSerializer

class PayoutScheduleViewSet(viewsets.ModelViewSet):
    queryset = PayoutSchedule.objects.all()
    serializer_class = PayoutScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]  # tighten later
