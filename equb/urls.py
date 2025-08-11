from rest_framework.routers import DefaultRouter
from .views.equb_group_view import EqubGroupViewSet
from .views.group_member_view import GroupMemberViewSet

router = DefaultRouter()
router.register(r"equb-groups", EqubGroupViewSet, basename="equbgroup")
router.register(r"group-members", GroupMemberViewSet, basename="groupmember")

urlpatterns = router.urls
