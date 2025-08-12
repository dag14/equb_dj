from rest_framework.routers import DefaultRouter
from .views.equb_group_view import EqubGroupViewSet
from .views.group_member_view import GroupMemberViewSet
from .views.ContributionViewSet import ContributionViewSet
from .views.PayoutScheduleViewSet import PayoutScheduleViewSet

router = DefaultRouter()
router.register(r"equb-groups", EqubGroupViewSet, basename="equbgroup")
router.register(r"group-members", GroupMemberViewSet, basename="groupmember")
router.register(r"contributions", ContributionViewSet, basename="contribution")
router.register(r"payout-schedules", PayoutScheduleViewSet, basename="payoutschedule")

urlpatterns = router.urls
