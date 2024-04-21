# ruff: noqa
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import TransferViewSet
from .views import product_unitViewSet
from .views import productViewSet
from .views import qrViewSet
from .views import refresh_api
from .views import refresh_api_unit

router = DefaultRouter()
router.register(r"products", productViewSet, basename="product")
router.register(r"QR", qrViewSet)
router.register(r"transfers", TransferViewSet)
router.register(r"productunits", product_unitViewSet)

urlpatterns = [
    path("refresh-api/", refresh_api, name="refresh_api"),
    path("refresh_api_unit/", refresh_api_unit, name="refresh_api_unit"),
] + router.urls
