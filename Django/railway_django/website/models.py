from django.db import models
from django.conf import settings
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class unit(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class unit_frac(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class productunit(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
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
        return self.Smacc_Code
    

class qr(models.Model):
    wh = models.ForeignKey(wh, on_delete=models.CASCADE)
    productunit = models.ForeignKey(productunit, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate QR code and save it here
        qr_info = f"WH: {self.wh.id}, ProductUnit: {self.productunit.id}, Quantity: {self.quantity}, Created: {self.created_at}"
        qr_img = qrcode.make(qr_info)
        qr_io = BytesIO()
        qr_img.save(qr_io, format='JPEG')
        self.qr_code.save(f"qr_code_{self.pk}.jpg", File(qr_io), save=False)
        
        super().save(*args, **kwargs)  # Call the "real" save() method.
    

    def __str__(self):
        return f"{self.wh} - {self.productunit} - {self.quantity}"

class TransportGroup(models.Model):
    name = models.CharField(max_length=100)
    # Add any other fields relevant to your transport group here

    def __str__(self):
        return self.name

class Transport(models.Model):
    From = models.ForeignKey('WH', on_delete=models.CASCADE, related_name='transport_from')
    To = models.ForeignKey('TransportGroup', on_delete=models.CASCADE, related_name='transport_to')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    #array of image
    
    def __str__(self):
        return f"From {self.From} To {self.To}"
    
class TransportImage(models.Model):
    transport = models.ForeignKey(Transport, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='transport_images/')


class whtype(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# class Users(models.Model):
#     products = models.ManyToManyField(Product)

#     def __str__(self):
#         # Join all related product names into a single string
#         return ', '.join([product.name for product in self.products.all()])

    # Add any other fields relevant to your transport group here

    def __str__(self):
        return self.name

class ProductPicked1(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    smaccFrom = models.ForeignKey(wh, on_delete=models.CASCADE, null=True, related_name='smacc_from')
    smaccTo = models.ForeignKey(wh, on_delete=models.CASCADE, null=True, related_name='smacc_to')
    

    def smaccFrom_code(self):
        return self.smaccFrom.Smacc_Code if self.smaccFrom else ''
 
    def smaccTo_code(self):
        return self.smaccTo.Smacc_Code if self.smaccTo else ''

    def smaccFrom_name(self):
        return self.smaccFrom.name if self.smaccFrom else ''

    def smaccTo_name(self):
        return self.smaccTo.name if self.smaccTo else ''





















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