from rest_framework import serializers
from equb.models import PayoutSchedule

class PayoutScheduleSerializer(serializers.ModelSerializer):
    recipient_username = serializers.CharField(source="recipient.user.username", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = PayoutSchedule
        fields = [
            "id",
            "group",
            "group_name",
            "recipient",
            "recipient_username",
            "cycle_number",
            "amount",
            "scheduled_date",
            "actual_date",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
