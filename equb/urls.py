from rest_framework.routers import DefaultRouter
from .views.equb_group_view import EqubGroupViewSet
from .views.group_member_view import GroupMemberViewSet
from .views.contribution_view import ContributionViewSet
from .views.payout_schedule_view import PayoutScheduleViewSet
from .views.penalty_view import PenaltyViewSet

router = DefaultRouter()
router.register(r"equb-groups", EqubGroupViewSet, basename="equbgroup")
router.register(r"group-members", GroupMemberViewSet, basename="groupmember")
router.register(r"contributions", ContributionViewSet, basename="contribution")
router.register(r"payout-schedules", PayoutScheduleViewSet, basename="payoutschedule")
router.register(r"penalties", PenaltyViewSet,basename="penalty")

urlpatterns = router.urls
