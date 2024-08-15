from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html

from .models import Product
from .models import ProductUnit
from .models import Qr
from .models import Track
from .models import Transfer
from .models import Unit
from .models import Wh
from .models import WhType
from .models import Zpl


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


@admin.action(
    description="Toggle selected product statuses",
)
def toggle_status(modeladmin, request, queryset):
    for product in queryset:
        product.is_active = not product.is_active
        product.save()
    modeladmin.message_user(request, ("Selected product statuses have been toggled."))


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
    actions = [toggle_status]  # Register the custom action


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


@admin.register(Zpl)
class ZplAdmin(admin.ModelAdmin):
    readonly_fields = ["qr", "zpl_code", "random_id", "created_at", "updated_at"]
    list_display = ["qr", "zpl_code", "random_id", "created_at", "updated_at"]


class ZplInline(admin.TabularInline):
    model = Zpl
    extra = 0
    readonly_fields = ("zpl_code",)


@admin.register(Qr)
class QrAdmin(admin.ModelAdmin):
    list_display = (
        "wh",
        "productunit",
        "quantity",
        "created_at",
        "updated_at",
        "download_zpl_link",
    )
    exclude = ("created_at", "updated_at")
    autocomplete_fields = ["productunit"]  # Enable autocomplete here

    @admin.display(
        description="Download ZPL",
    )
    def download_zpl_link(self, obj):
        return format_html(
            '<a href="{}">Download ZPL</a>',
            reverse("admin:download_zpl", args=[obj.id]),
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "download_zpl/<int:qr_id>/",
                self.admin_site.admin_view(self.download_single_zpl),
                name="download_zpl",
            ),
        ]
        return custom_urls + urls

    def download_single_zpl(self, request, qr_id):
        qr = Qr.objects.get(pk=qr_id)
        zpl_entries = Zpl.objects.filter(qr=qr)
        zpl_content = "\n".join(zpl.zpl_code for zpl in zpl_entries)

        response = HttpResponse(zpl_content, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename=zpl_codes_{qr_id}.txt"
        return response


@admin.register(WhType)
class WhtypeAdmin(admin.ModelAdmin):
    list_display = ("name",)  # Columns to display in the admin list view


class TransferInline(admin.TabularInline):
    model = Transfer
    exclude = ["from_warehouse_name", "to_warehouse_name"]
    extra = 1  # Defines how many rows are shown by default


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    inlines = [
        TransferInline,
    ]
    list_display = ("id", "pdf", "is_sent", "picture")
    exclude = ("pdf", "is_sent")

    def save_model(self, request, obj, form, change):
        # Generate PDF when saving from admin
        super().save_model(request, obj, form, change)
        obj.generate_pdf()
