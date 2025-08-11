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
            "max_members",
            "start_date",
            "end_date",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def validate_max_members(self, value):
        if value < 3:
            raise serializers.ValidationError("Equb group must have at least 3 members.")
        return value
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("start_date must be before end_date.")
        return data
