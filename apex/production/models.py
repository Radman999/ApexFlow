import random

from django.conf import settings
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
    item_code = models.CharField(max_length=10, default="", blank=True)
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


class Zpl(models.Model):
    qr = models.ForeignKey(
        "Qr",
        on_delete=models.CASCADE,
        related_name="zpls",
        null=True,
    )
    zpl_code = models.TextField()
    random_id = models.IntegerField(default=0, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.qr.productunit} - {self.qr.wh} - ({self.id})"

    def save(self, *args, **kwargs):
        if self._state.adding:  # Only run this logic when creating a new object
            while not self.random_id:
                potential_id = random.randint(10000000, 99999999)  # noqa: S311
                if not Zpl.objects.filter(random_id=potential_id).exists():
                    self.random_id = potential_id
            # Generate ZPL code after random_id is set
            self.zpl_code = self.create_zpl_data()
        super().save(*args, **kwargs)

    def create_zpl_data(self):
        formatted_date = self.created_at.strftime("%Y-%m-%d")
        zpl_product_name = (
            self.qr.productunit.product_name + " " + self.qr.productunit.unit_name
        )
        long_name = 30
        # Generate ZPL code including the random_id
        zpl_code = (
            "^XA"
            "^CI28"  # Set the encoding to UTF-8 for Unicode support
            "^CW1,E:TT003M_.FNT"  # Set the default font to Arabic font
            f"^FO10,3^BQN,2,9^FDQA,{self.random_id}^FS"
            f"^FO250,100^A0,30,30^FD{self.random_id}^FS"
            f"^FO250,150^A0,30,30^FD{formatted_date}^FS"
        )
        if len(zpl_product_name) > long_name:
            zpl_code += (
                f"^FO210,30^A1N,25,25^PA0,1,1,1^FD{zpl_product_name[:30]}^FS"
                f"^FO210,60^A1N,25,25^PA0,1,1,1^FD{zpl_product_name[30:]}^FS"
            )
        else:
            zpl_code += f"^FO210,30^A1N,25,25^PA0,1,1,1^FD{zpl_product_name}^FS"
        zpl_code += "^XZ"
        return zpl_code


class Qr(models.Model):
    wh = models.ForeignKey("Wh", on_delete=models.CASCADE, related_name="wh")
    productunit = models.ForeignKey("ProductUnit", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    create_zpl = True  # Default is to create Zpl instances.

    def __str__(self):
        return f"{self.wh} - {self.productunit} - ID: {self.id}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and self.create_zpl:
            self.create_related_zpl()

    def create_related_zpl(self):
        for _ in range(self.quantity):  # noqa: F402
            Zpl.objects.create(
                qr=self,
                created_at=self.created_at,
                updated_at=self.updated_at,
            )


class Track(models.Model):
    # This model acts as the parent, if needed additional fields can be added here
    def __str__(self):
        return f"Track {self.id}"


class Transfer(models.Model):
    reference = models.ForeignKey(
        "Track",
        on_delete=models.CASCADE,
        related_name="transfers",
    )
    From = models.ForeignKey(
        "Zpl",
        on_delete=models.CASCADE,
        related_name="transfer_from",
    )
    To = models.ForeignKey("Wh", on_delete=models.CASCADE, related_name="transfer_to")

    def __str__(self):
        return f"From {self.From} To {self.To}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Decrement the quantity of the original QR
            original_qr = self.From.qr
            if original_qr.quantity > 0:
                original_qr.quantity -= 1
                original_qr.save()

            # Check if the 'To' warehouse already has a corresponding Qr
            existing_qr = Qr.objects.filter(
                wh=self.To,
                productunit=self.From.qr.productunit,
                created_at=self.From.qr.created_at,
            ).first()

            if existing_qr:
                existing_qr.quantity += 1
                existing_qr.save()
                new_qr = existing_qr
            else:
                new_qr = Qr(
                    wh=self.To,
                    productunit=self.From.qr.productunit,
                    quantity=1,
                    created_at=self.From.qr.created_at,
                    updated_at=timezone.now(),
                )
                new_qr.create_zpl = False  # Prevent Zpl creation during save
                new_qr.save()

            # Update the Zpl's qr to the new or updated Qr instance
            self.From.qr = new_qr
            self.From.save()

            super().save(*args, **kwargs)


class WhType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
