from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models import F
from django.db import transaction
# Create your models here.

class product(models.Model):
    name = models.CharField(_('name'),max_length=100)
    is_active = models.BooleanField(_('Status'),default=False)
    category = models.CharField(_('category'), max_length=50, choices=[('finished', 'finished'), ('materials', 'materials'), ('services', 'services')])
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
    
    def __str__(self):
        return self.name

class product_unit(models.Model):
    tenant = models.IntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    product_unit_name = models.CharField(max_length=255, null=True, blank=True)
    unit_name = models.CharField(max_length=100, null=True, blank=True)
    remaining_quantity = models.IntegerField(null=True, blank=True)
    relative_remaining_quantity = models.IntegerField(null=True, blank=True)
    tier_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    picture = models.URLField(null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    unit_fraction = models.BigIntegerField(null=True, blank=True)
    old_cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)
    default = models.BooleanField(null=True, blank=True)
    sync_quantity_salla = models.BooleanField(null=True, blank=True)
    quantity_salla = models.BigIntegerField(null=True, blank=True)
    auto_add = models.BooleanField(null=True, blank=True)
    item_code = models.CharField(max_length=100, null=True, blank=True)
    related_item_code = models.JSONField(default=list, null=True, blank=True)
    product = models.IntegerField(null=True, blank=True)
    unit = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.product_unit_name

class creator(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True  # Important: This makes the model abstract

class test(creator):
    name = models.CharField(max_length=100)




class unit(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('unit')
        verbose_name_plural = _('units')
    
    def __str__(self):
        return self.name
    
class unit_frac(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class productunit(models.Model):
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    unit = models.ForeignKey(unit, on_delete=models.CASCADE)
    unit_frac = models.ForeignKey(unit_frac, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    item_code = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to='product_units/', blank=True, null=True)  # New field
    
    def __str__(self):
        return self.product.name + ' - ' + self.unit.name + ' - ' + self.unit_frac.name

class wh(models.Model):
    name = models.CharField(max_length=100)
    Smacc_Code = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name + ' ' + self.Smacc_Code
    

class qr(models.Model):
    wh = models.ForeignKey('wh', on_delete=models.CASCADE, related_name="wh")
    productunit = models.ForeignKey('product_unit', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
 #   qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
 #   id_t = models.IntegerField(null=True, blank=True)  # New field to mirror the id

 #   def save(self, *args, **kwargs):
 #       creating = self.pk is None  # Check if the instance is being created
 #       super().save(*args, **kwargs)  # Call the "real" save() method.
 #       if creating:
 #           self.generate_qr_code()
 #           self.id_t = self.pk  # Assign the PK to id_t after the object is saved
 #           super().save(update_fields=['id_t'])  # Save again to update id_t
#
 #   def generate_qr_code(self):
 #       local_datetime = timezone.localtime(self.created_at, timezone=timezone.get_fixed_timezone(180))  # Riyadh is UTC+3
 #       formatted_date = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
 #       qr_info = f"WH: {self.wh.id}, ProductUnit: {self.productunit.id}, Quantity: {self.quantity}, Created: {formatted_date}"
 #       qr_img = qrcode.make(qr_info)
 #       qr_io = BytesIO()
 #       qr_img.save(qr_io, format='JPEG')
 #       qr_io.seek(0)
 #       self.qr_code.save(f"qr_code_{self.pk}.jpg", ContentFile(qr_io.read()), save=False)

    def __str__(self):
        return f"{self.wh} - {self.productunit} - Quantity: ({self.quantity})"







#class warehouse(models.Model):
#    name = models.ForeignKey('wh', on_delete=models.CASCADE, related_name="warehouse_entries")
#    quantity = models.IntegerField()

#    def __str__(self):
#        return f"{self.name} - Quantity: {self.quantity}"

class Transfer(models.Model):
    From = models.ForeignKey(qr, on_delete=models.CASCADE, related_name="transfer_from")
    To = models.ForeignKey(wh, on_delete=models.CASCADE, related_name="transfer_to")
    quantity = models.IntegerField()
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Check if there's an existing qr entry for the 'To' wh and 'From.productunit'
            existing_qr = qr.objects.filter(wh=self.To, productunit=self.From.productunit,created_at=self.From.created_at).first()
            if existing_qr:
                # If exists, update the quantity
                if self.From.quantity >= self.quantity:
                    self.From.quantity = F('quantity') - self.quantity
                    self.From.save()
                    existing_qr.quantity = F('quantity') + self.quantity
                    existing_qr.save()
                else:
                    raise ValueError("Not enough stock in source warehouse to complete transfer.")
            else:
                # If not, create a new qr entry
                if self.From.quantity >= self.quantity:
                    self.From.quantity = F('quantity') - self.quantity
                    self.From.save()
                    new_qr = qr.objects.create(
                        wh=self.To,
                        productunit=self.From.productunit,
                        quantity=self.quantity,
                        created_at=self.From.created_at,
                        updated_at=self.From.updated_at
                    )
                else:
                    raise ValueError("Not enough stock in source warehouse to complete transfer.")

            # Proceed with saving the Transfer
            super(Transfer, self).save(*args, **kwargs)








#    def save(self, *args, **kwargs):
#        if self.From.quantity >= self.quantity:  # Ensuring there is enough quantity to transfer
#            self.From.quantity -= self.quantity
#            self.To.quantity += self.quantity
#            self.From.save()
#            self.To.save()
#            super().save(*args, **kwargs)
#        else:
#            raise ValueError("Not enough stock in source warehouse to complete transfer.")






# class Transport(models.Model):
#     From = models.ForeignKey('wh', on_delete=models.CASCADE, related_name='transport_from')
#     To = models.ForeignKey('wh', on_delete=models.CASCADE, related_name='transport_to')
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)
#     image = models.ImageField(upload_to='Transport/', blank=True, null=True)

#     def __str__(self):
#         return f"From {self.From} To {self.To}"

#     def perform_transport(self, quantity):
#         qr_items = qr.objects.filter(wh=self.From)
#         for item in qr_items:
#             if item.quantity < quantity:
#                 continue  # Optionally, handle the error more robustly

#             target_item, created = qr.objects.get_or_create(
#                 wh=self.To,
#                 productunit=item.productunit,
#                 defaults={'quantity': 0, 'created_at': timezone.now(), 'updated_at': timezone.now()}
#             )
#             target_item.quantity = F('quantity') + quantity
#             target_item.save()

#             item.quantity -= quantity
#             item.save()
    
  #  To = models.ForeignKey('WH', on_delete=models.CASCADE, related_name='transport_to')
  #  image = models.ImageField(upload_to='Transport/', blank=True, null=True)  # New field


class whtype(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




















# class Post(models.Model):
#     author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     title = models.CharField(max_length=200)
#     text = models.TextField()
#     created_date = models.DateTimeField(default=timezone.now)
#     published_date = models.DateTimeField(blank=True, null=True)

#     def publish(self):
#         self.published_date = timezone.now()
#         self.save()

#     def __str__(self):
#         return self.title