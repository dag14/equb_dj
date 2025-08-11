from rest_framework import serializers
from equb.models import EqubGroup

class EqubGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EqubGroup
        fields = [
            "id",
            "name",
            "description",
            "status",
            "rotation_rule",
            "contribution_amount",
            "total_cycles",
            "current_cycle",
            "created_at",
            "started_at",
            "completed_at",
            "admin",
        ]
        read_only_fields = ["status", "created_at", "started_at", "completed_at", "current_cycle"]

    def validate_total_cycles(self, value):
        if value < 1:
            raise serializers.ValidationError("Total cycles must be at least 1.")
        return value

    def validate_contribution_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Contribution amount must be positive.")
        return value

    def validate(self, data):
        started_at = data.get('started_at')
        completed_at = data.get('completed_at')
        if started_at and completed_at and started_at >= completed_at:
            raise serializers.ValidationError("started_at must be before completed_at.")
        return data

