from rest_framework.routers import DefaultRouter
from .views.equb_group_view import EqubGroupViewSet

router = DefaultRouter()
router.register(r"equb-groups", EqubGroupViewSet, basename="equbgroup")

urlpatterns = router.urls
