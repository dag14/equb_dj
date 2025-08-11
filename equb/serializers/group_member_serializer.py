from rest_framework import serializers
from equb.models import GroupMember

class GroupMemberSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = GroupMember
        fields = [
            "id",
            "user",
            "user_username",
            "group",
            "group_name",
            "role",
            "status",
            "joined_at"
        ]
        read_only_fields = ["joined_at"]
    def validate(self, data):
        """
        Prevent duplicate memberships for the same user & group.
        """
        user = data.get("user")
        group = data.get("group")

        if user and group:
            qs = GroupMember.objects.filter(user=user, group=group)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "This user is already a member of the selected group."
                )
        return data
    def validate_role(self, value):
        if value not in dict(GroupMember.ROLE_CHOICES):
            raise serializers.ValidationError("Invalid role.")
        return value

    def validate_status(self, value):
        if value not in dict(GroupMember.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status.")
        return value