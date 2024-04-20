from django.contrib import admin
from django.shortcuts import redirect, render
from .models import product
from .models import unit
from .models import productunit
from .models import unit_frac
from django.utils.html import format_html
from .models import wh, whtype
from .models import qr
# from .models import Transport
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.db import transaction
from django.contrib.admin.utils import unquote
from django.contrib.admin.options import IS_POPUP_VAR
from .models import Transfer
from .models import test
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
    list_display = ('name', 'status', 'created_at', 'updated_at',)  # Columns to display in the admin list view
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

#    def qr_code_tag(self, obj):
#        if obj.qr_code:
#            return format_html('<img src="{}" style="width: 45px; height:auto;">', obj.qr_code.url)
#        return "No QR Code"
#    qr_code_tag.short_description = 'QR Code'
#
admin.site.register(qr, qrAdmin)

# class TransportAdmin(admin.ModelAdmin):
#     list_display = ('From', 'To', 'created_at', 'updated_at', 'transport_link')

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('<int:object_id>/transfer/', self.admin_site.admin_view(self.transfer_view), name='transport-transfer'),
#         ]
#         return custom_urls + urls

#     def transport_link(self, obj):
#         # Generate the URL for the custom view
#         url = reverse('admin:transport-transfer', args=[obj.pk])
#         # Return a HTML link
#         return format_html('<a href="{}">Perform Transport</a>', url)
#     transport_link.short_description = 'Perform Transport'


#     def transfer_view(self, request, object_id):
#         transport = self.get_object(request, object_id)
#         if request.method == 'POST':
#             form = TransferQuantityForm(request.POST)
#             if form.is_valid():
#                 quantity = form.cleaned_data['quantity']
#                 transport.perform_transport(quantity)
#                 self.message_user(request, f"Transport successful for {quantity} units.")
#                 return redirect('admin:index')
#         else:
#             form = TransferQuantityForm()

#         context = {
#             'form': form,
#             'opts': self.model._meta,
#             'original': transport,
#             'title': 'Transfer Quantity',
#         }
#         return render(request, "admin/transfer_quantity.html", context)


# admin.site.register(Transport, TransportAdmin)



  #  def image_tag(self, obj):
  #      if obj.image:
  #          return format_html('<img src="{}" style="width: 45px; height:auto;">', obj.image.url)
  #      return "No Image"
  #  image_tag.short_description = 'Image'

#, 'image_tag'

class whtypeAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Columns to display in the admin list view


admin.site.register(product, productAdmin)
admin.site.register(unit, UnitAdmin)
admin.site.register(productunit, productunitAdmin)
admin.site.register(unit_frac, unit_fracAdmin)
admin.site.register(wh, whAdmin)
admin.site.register(whtype, whtypeAdmin)

