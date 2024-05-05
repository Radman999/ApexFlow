from io import BytesIO

import qrcode
from django.conf import settings
from django.core.files import File
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Product(models.Model):
    name = models.CharField(_("name"), max_length=100)
    is_active = models.BooleanField(_("Status"), default=False)
    category = models.CharField(
        _("category"),
        max_length=50,
        choices=[
            ("finished", "finished"),
            ("materials", "materials"),
            ("services", "services"),
        ],
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self):
        return self.name


class ProductUnit(models.Model):
    tenant = models.IntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=255, default="", blank=True)
    product_unit_name = models.CharField(max_length=255, default="", blank=True)
    unit_name = models.CharField(max_length=100, default="", blank=True)
    remaining_quantity = models.IntegerField(null=True, blank=True)
    relative_remaining_quantity = models.IntegerField(null=True, blank=True)
    tier_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(blank=True)
    modified = models.DateTimeField(blank=True)
    picture = models.URLField(default="", blank=True, null=True)  # noqa: DJ001
    sku = models.CharField(default="", blank=True, null=True)  # noqa: DJ001
    unit_fraction = models.BigIntegerField(null=True, blank=True)
    old_cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(null=True, blank=True)
    default = models.BooleanField(null=True, blank=True)
    sync_quantity_salla = models.BooleanField(null=True, blank=True)
    quantity_salla = models.BigIntegerField(null=True, blank=True)
    auto_add = models.BooleanField(null=True, blank=True)
    item_code = models.BigIntegerField(null=True, blank=True)
    related_item_code = models.JSONField(null=True, default=dict, blank=True)
    product = models.IntegerField(null=True, blank=True)
    unit = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.product_unit_name


class Creator(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True  # Important: This makes the model abstract


class Test(Creator):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("unit")
        verbose_name_plural = _("units")

    def __str__(self):
        return self.name


class Wh(models.Model):
    name = models.CharField(max_length=100)
    Smacc_Code = models.CharField(max_length=100)

    def __str__(self):
        return self.name + " " + self.Smacc_Code


class Qr(models.Model):
    wh = models.ForeignKey("wh", on_delete=models.CASCADE, related_name="wh")
    productunit = models.ForeignKey("ProductUnit", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    generate_qr_flag = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.wh} - {self.productunit} - Quantity: ({self.quantity})"

    def save(self, *args, **kwargs):
        # Call the real save() method first to ensure the model is saved to the DB
        super().save(*args, **kwargs)

        # Check if the qr_code already exists to avoid regenerating it unnecessarily
        # Only generate a QR code if the flag is True
        if self.generate_qr_flag and not self.qr_code:
            self.generate_qr_code()
            super().save(*args, **kwargs)  # Save again with the QR code

    def generate_qr_code(self):
        """Generates a QR code and attaches it to the qr_code field."""
        api = f"/api/QR/{self.id}/"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(api)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        fname = f"qr_code-{self.id}.png"
        buffer = BytesIO()
        img.save(buffer, "PNG")
        self.qr_code.save(fname, File(buffer), save=False)
        buffer.close()


class Track(models.Model):
    # This model acts as the parent, if needed additional fields can be added here
    def __str__(self):
        return f"Track {self.id}"


class Transfer(models.Model):
    reference = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name="transfers",
    )
    From = models.ForeignKey(Qr, on_delete=models.CASCADE, related_name="transfer_from")
    To = models.ForeignKey(Wh, on_delete=models.CASCADE, related_name="transfer_to")
    quantity = models.IntegerField()

    def __str__(self):
        return f"From {self.From} To {self.To}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Disable QR code generation during transfer process
            self.From.generate_qr_flag = False
            self.From.save()

            # Logic to handle transferring items
            if self.From.quantity >= self.quantity:
                self.From.quantity -= self.quantity
                self.From.save()

                # Update or create Qr for 'To'
                existing_qr = Qr.objects.filter(
                    wh=self.To,
                    productunit=self.From.productunit,
                    created_at=self.From.created_at,
                ).first()

                if existing_qr:
                    existing_qr.quantity += self.quantity
                    existing_qr.generate_qr_flag = (
                        False  # Ensure not to generate QR code
                    )
                    existing_qr.save()
                else:
                    Qr.objects.create(
                        wh=self.To,
                        productunit=self.From.productunit,
                        quantity=self.quantity,
                        created_at=self.From.created_at,
                        updated_at=self.From.updated_at,
                        qr_code=None,
                        generate_qr_flag=False,  # Prevent QR code generation
                    )
            else:
                error_message = "Not enough stock to complete the transfer."
                raise ValueError(error_message)

            # Restore QR code generation flag and save the Transfer
            self.From.generate_qr_flag = True
            super().save(*args, **kwargs)


class WhType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
