from django.contrib import admin
from django.shortcuts import redirect, render
from .models import product
from .models import unit
from .models import productunit
from .models import unit_frac
from django.utils.html import format_html
from .models import wh, whtype
from .models import qr
from django.urls import path, reverse
from django.db import transaction
from django.contrib.admin.utils import unquote
from django.contrib.admin.options import IS_POPUP_VAR
from .models import Transfer
from .models import test
from django.utils.html import format_html
from django.utils.html import mark_safe
from .models import product_unit

class product_unitAdmin(admin.ModelAdmin):
    list_display = ('product_unit_name', 'get_image', 'unit_name','item_code',
                  'created', 'modified', 'sku',
                  'unit_fraction', 'old_cost_price', 'is_active', 'default', 'sync_quantity_salla',
                  'quantity_salla', 'auto_add', 'related_item_code', 'product', 'unit')  # Columns to display in the admin list view
    search_fields = ('product_unit_name', 'unit_name')  # Add a search bar to the admin list view
    def get_image(self, obj):
        return mark_safe(f'<img src="{obj.picture}" width="100" height="100" />')
    get_image.short_description = 'Picture'  # Sets the column name


admin.site.register(product_unit, product_unitAdmin)

class TransferAdmin(admin.ModelAdmin):
    list_display = ('From', 'To', 'quantity')  # Columns to display in the admin list view


admin.site.register(Transfer, TransferAdmin)


#from .models import warehouse

#class warehouseAdmin(admin.ModelAdmin):
#    list_display = ('name', 'quantity')

#admin.site.register(warehouse, warehouseAdmin)
class creatorAdmin(admin.ModelAdmin):
    exclude = ('creator', 'created_at', 'updated_at')  # Exclude these fields from the admin form

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Check if the object is being created
            obj.creator = request.user  # Set the creator to the current user
        super().save_model(request, obj, form, change)


class testAdmin(creatorAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'creator')  # Columns to display in the admin list view

admin.site.register(test, testAdmin)
class productAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active','category', 'created_at', 'updated_at',)  # Columns to display in the admin list view
    search_fields = ('name',)  # Add a search bar to the admin list view
    exclude = ('created_at','updated_at')

class UnitAdmin(creatorAdmin):
    list_display = ('name', 'created_at', 'updated_at','creator')  # Columns to display in the admin list view
    exclude = ('created_at','updated_at')
class productunitAdmin(admin.ModelAdmin):
    list_display = ('product', 'unit', 'unit_frac', 'item_code', 'created_at', 'updated_at', 'image_tag')  # Columns to display in the admin list view
    readonly_fields = ('created_at', 'updated_at', 'image_tag')  # Make these fields read-only
    



    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:auto;">', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Image'

class unit_fracAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')  # Columns to display in the admin list view
    readonly_fields = ('created_at', 'updated_at')  # Make these fields read-only

class whAdmin(admin.ModelAdmin):
    list_display = ('name', 'Smacc_Code')  # Columns to display in the admin list view

class qrAdmin(admin.ModelAdmin):
    list_display = ('wh', 'productunit', 'quantity', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['productunit']  # Enable autocomplete here

admin.site.register(qr, qrAdmin)

class whtypeAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Columns to display in the admin list view


admin.site.register(product, productAdmin)
admin.site.register(unit, UnitAdmin)
admin.site.register(productunit, productunitAdmin)
admin.site.register(unit_frac, unit_fracAdmin)
admin.site.register(wh, whAdmin)
admin.site.register(whtype, whtypeAdmin)

