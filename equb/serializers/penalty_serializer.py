from rest_framework import serializers
from equb.models import Penalty

class PenaltySerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source="member.user.username", read_only=True)
    group_name = serializers.CharField(source="member.group.name", read_only=True)

    class Meta:
        model = Penalty
        fields = [
            "id",  
            "member",
            "member_username",
            "group_name",
            "reason",
            "amount",
            "issued_at",
            "status"
        ]
        read_only_fields = ["issued_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Penalty amount must be greater than zero.")
        return value

    def validate_status(self, value):
        if value not in dict(Penalty.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid penalty status.")
        return value
