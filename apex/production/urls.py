# ruff: noqa
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import TransferViewSet
from .views import ProductUnitViewSet
from .views import ProductViewSet
from .views import QrViewSet
from .views import refresh_api
from .views import refresh_api_unit
from .views import WhViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"QR", QrViewSet)
router.register(r"transfers", TransferViewSet)
router.register(r"productunits", ProductUnitViewSet)
router.register(r"wh", WhViewSet)

urlpatterns = [
    path("refresh-api/", refresh_api, name="refresh_api"),
    path("refresh_api_unit/", refresh_api_unit, name="refresh_api_unit"),
] + router.urls
