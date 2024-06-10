from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProductUnitViewSet
from .views import ProductViewSet
from .views import QrViewSet
from .views import TrackViewSet
from .views import TransferViewSet
from .views import WhViewSet
from .views import ZplViewSet
from .views import refresh_api
from .views import refresh_api_unit

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"QR", QrViewSet)
router.register(r"transfers", TransferViewSet)
router.register(r"productunits", ProductUnitViewSet)
router.register(r"wh", WhViewSet)
router.register(r"Track", TrackViewSet)
router.register(r"ZPL", ZplViewSet)

urlpatterns = [
    path("refresh-api/", refresh_api, name="refresh_api"),
    path("refresh_api_unit/", refresh_api_unit, name="refresh_api_unit"),
    *router.urls,
]
