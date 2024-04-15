from django.contrib import admin
from .models import Product
from .models import unit
from .models import productunit
from .models import unit_frac
from django.utils.html import format_html
from .models import wh, whtype
from .models import qr
from .models import TransportGroup
from .models import Transport, TransportImage
# from .models import smaccGroup
# from .models import Users
from .models import ProductPicked1

# from .models import Post

# Register your models here.
class InputAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at', 'updated_at')  # Columns to display in the admin list view
    readonly_fields = ('created_at', 'updated_at')  # Make these fields read-only

class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')  # Columns to display in the admin list view
    readonly_fields = ('created_at', 'updated_at')  # Make these fields read-only

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
    list_display = ('wh', 'productunit', 'quantity', 'created_at', 'updated_at', 'qr_code_tag')  # Columns to display in the admin list view
    readonly_fields = ('created_at', 'updated_at', 'qr_code_tag')  # Make these fields read-only

    def qr_code_tag(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" style="width: 45px; height:auto;">', obj.qr_code.url)
        return "No QR Code"
    qr_code_tag.short_description = 'QR Code'






class TransportAdmin(admin.ModelAdmin):
    list_display = ('From', 'To', 'created_at', 'updated_at' )  # Columns to display in the admin list view
    readonly_fields = ('created_at', 'updated_at')  # Make these fields read-only



class TransportImageInline(admin.TabularInline):
    model = TransportImage
    extra = 1  # Number of empty forms to display

@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ('From', 'To', 'show_images', 'created_at', 'updated_at',)

    readonly_fields = ('created_at', 'updated_at',)
    inlines = [TransportImageInline]

    def show_images(self, obj):
        images = obj.images.all()[:5]  # Limit the number of images to prevent performance issues
        html = ''
        for img in images:
            html += '<img src="{}" style="width: 45px; height:auto; margin-right: 5px;">'.format(img.image.url)
        return format_html(html)
    show_images.short_description = 'Images'

@admin.register(TransportImage)
class TransportImageAdmin(admin.ModelAdmin):
    pass


@admin.register(whtype)
class whtypeAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Columns to display in the admin list view


class ProductPicked1Admin(admin.ModelAdmin):
    list_display = ('product', 'get_smaccFrom_code', 'get_smaccTo_code')


    def get_smaccFrom_code(self, obj):
        return obj.smaccFrom.Smacc_Code if obj.smaccFrom else '-'
    get_smaccFrom_code.short_description = 'Smacc From Code'  # Sets column name

    def get_smaccTo_code(self, obj):
        return obj.smaccTo.Smacc_Code if obj.smaccTo else '-'
    get_smaccTo_code.short_description = 'Smacc To Code'  # Sets column name



# @admin.register(Users)
# class UsersAdmin(admin.ModelAdmin):
#     list_display = ('name', 'status')  # Columns to display in the admin list view


# admin.site.register(smaccGroup)
admin.site.register(ProductPicked1, ProductPicked1Admin)
admin.site.register(Product, InputAdmin)
admin.site.register(unit, UnitAdmin)
admin.site.register(productunit, productunitAdmin)
admin.site.register(unit_frac, unit_fracAdmin)
admin.site.register(wh, whAdmin)
admin.site.register(qr, qrAdmin)
admin.site.register(TransportGroup)
# admin.site.register(Transport)




# admin.site.register(Post)