from rest_framework import serializers
from equb.models import Contribution

class ContributionSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source="member.user.username", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = Contribution
        fields = [
            "id",
            "group",
            "group_name",
            "member",
            "member_username",
            "cycle_number",
            "amount",
            "status",
            "payment_date",
            "recorded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        
        return data
