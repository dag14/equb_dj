from rest_framework import serializers
from equb.models import EqubGroup, GroupMember
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number"]

class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupMember
        fields = ["id", "role", "status", "contributions", "has_won", "user"]

class EqubGroupSerializer(serializers.ModelSerializer):
    total_members = serializers.IntegerField(read_only=True)
    members = GroupMemberSerializer(source="memberships", many=True, read_only=True)

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
            "total_members",
            "members",  # 👈 now included
        ]
        read_only_fields = [
            "status",
            "created_at",
            "started_at",
            "completed_at",
            "current_cycle",
            "admin",
            "total_members",
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['admin'] = user
        else:
            validated_data['admin'] = None
        return super().create(validated_data)

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

    def get_total_members(self, obj):
        return obj.memberships.count()
