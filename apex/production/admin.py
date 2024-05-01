from django.contrib import admin
from django.utils.html import format_html

from .models import Product
from .models import ProductUnit
from .models import Qr
from .models import Test
from .models import Transfer
from .models import Unit
from .models import Wh
from .models import WhType


@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = (
        "product_unit_name",
        "get_image",
        "unit_name",
        "item_code",
        "created",
        "modified",
        "sku",
        "unit_fraction",
        "old_cost_price",
        "is_active",
        "default",
        "sync_quantity_salla",
        "quantity_salla",
        "auto_add",
        "related_item_code",
        "product",
        "unit",
    )  # Columns to display in the admin list view
    search_fields = (
        "product_unit_name",
        "unit_name",
    )  # Add a search bar to the admin list view

    @admin.display(
        description="Picture",
    )
    def get_image(self, obj):
        if obj.picture:
            return format_html('<img src="{}" width="100" height="100" />', obj.picture)
        return "No Image"


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = (
        "From",
        "To",
        "quantity",
    )  # Columns to display in the admin list view


class CreatorAdmin(admin.ModelAdmin):
    exclude = (
        "creator",
        "created_at",
        "updated_at",
    )  # Exclude these fields from the admin form

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Check if the object is being created
            obj.creator = request.user  # Set the creator to the current user
        super().save_model(request, obj, form, change)


@admin.register(Test)
class TestAdmin(CreatorAdmin):
    list_display = (
        "name",
        "created_at",
        "updated_at",
        "creator",
    )  # Columns to display in the admin list view


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "category",
        "created_at",
        "updated_at",
    )  # Columns to display in the admin list view
    search_fields = ("name",)  # Add a search bar to the admin list view
    exclude = ("created_at", "updated_at")


@admin.register(Unit)
class UnitAdmin(CreatorAdmin):
    list_display = (
        "name",
        "created_at",
        "updated_at",
        "creator",
    )  # Columns to display in the admin list view
    exclude = ("created_at", "updated_at")


@admin.register(Wh)
class WhAdmin(admin.ModelAdmin):
    list_display = ("name", "Smacc_Code")  # Columns to display in the admin list view


@admin.register(Qr)
class QrAdmin(admin.ModelAdmin):
    list_display = (
        "wh",
        "productunit",
        "quantity",
        "created_at",
        "updated_at",
        "qr_code_image",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ["productunit"]  # Enable autocomplete here

    def qr_code_image(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="100" height="100"/>', obj.qr_code.url,
            )
        return "No image"

    qr_code_image.short_description = "QR Code"


@admin.register(WhType)
class WhtypeAdmin(admin.ModelAdmin):
    list_display = ("name",)  # Columns to display in the admin list view
