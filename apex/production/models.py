import io
import random

import arabic_reshaper
from bidi.algorithm import get_display
from django.conf import settings
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import TableStyle


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
    pdf = models.FileField(upload_to="pdfs/", null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    picture = models.FileField(upload_to="pdfs/", null=True, blank=True)

    def __str__(self):
        return f"Track {self.id}"

    def save(self, *args, **kwargs):
        initial_save = not self.pk
        super().save(*args, **kwargs)

        # Only generate PDF if this is the initial save
        if initial_save:
            # Delay the PDF generation to ensure all related transfers are created
            self._generate_pdf_delayed()

    def _generate_pdf_delayed(self):
        # Use a transaction to delay the PDF generation
        transaction.on_commit(self.generate_pdf)

    def generate_pdf(self):  # noqa: PLR0915
        # Register a font that supports Arabic
        pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
        # Initialize transfers list
        transfers = []
        idx = 0
        from_warehouse = "Unknown"
        to_warehouse = "Unknown"
        # Collect transfer data
        for idx, transfer in enumerate(self.transfers.all(), start=1):  # noqa: B007
            product_unit_name = transfer.From.qr.productunit.product_unit_name
            existing_product = next(
                (
                    item
                    for item in transfers
                    if item["product_name"] == product_unit_name
                ),
                None,
            )
            from_warehouse = transfer.from_warehouse_name  # Use captured name
            to_warehouse = transfer.to_warehouse_name  # Use captured name
            if existing_product:
                existing_product["quantity"] += 1
            else:
                transfers.append(
                    {
                        "product_name": product_unit_name,
                        "quantity": 1,
                        "notes": "",  # Assuming each qr has a quantity and notes field
                    },
                )

        def register_fonts():
            """Register fonts required for the PDF."""
            pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))

        def create_styles():
            """Create and return custom styles for the PDF."""
            styles = getSampleStyleSheet()
            arabic_text_style = ParagraphStyle(
                "ArabicStyle",
                parent=styles["Normal"],
                fontName="Arial",
                fontSize=12,
                alignment=2,  # Right alignment
            )
            title_style = ParagraphStyle(
                "TitleStyle",
                parent=styles["Normal"],
                alignment=1,  # Center alignment
                fontName="Arial",
                fontSize=12,
            )
            return arabic_text_style, title_style

        def create_paragraph(text, style):
            """Create a Paragraph with reshaped and bidirectional text."""
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return Paragraph(bidi_text, style)

        def create_table(data, col_widths, row_heights=None, style_commands=None):
            """Create a table with the given data, column widths, and styles."""
            table = Table(data, colWidths=col_widths, rowHeights=row_heights)
            table_style = TableStyle(
                style_commands
                or [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ],
            )
            table.setStyle(table_style)
            return table

        def create_document():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []

            register_fonts()
            arabic_text_style, title_style = create_styles()

            title = create_paragraph("تحميل من المكتب", title_style)
            current_datetime = timezone.now().strftime("%Y-%m-%d")
            date = create_paragraph(f"التاريخ: {current_datetime}", arabic_text_style)

            # Create header row
            header_data = ["ملاحظات", "عدد الكراتين", "اسم المنتج", "#"]
            reshaped_header_data = [
                create_paragraph(item, arabic_text_style) for item in header_data
            ]
            data = [reshaped_header_data]

            # Add transfer data
            for transfer_idx, transfer in enumerate(transfers, start=1):
                data.append(
                    [
                        create_paragraph(transfer["notes"], arabic_text_style),
                        transfer["quantity"],
                        create_paragraph(transfer["product_name"], arabic_text_style),
                        transfer_idx,
                    ],
                )

            # Add space and signature rows
            space = create_table(
                [[""]],
                [430],
                [15],
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.gray),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ],
            )

            sign_data = [
                [
                    "",
                    create_paragraph(
                        f"اسم المستلم: {from_warehouse}",
                        arabic_text_style,
                    ),
                    idx + 1,
                ],
                ["", create_paragraph("التوقيع:", arabic_text_style), idx + 2],
                [
                    "",
                    create_paragraph(f"اسم المسلم: {to_warehouse}", arabic_text_style),
                    idx + 3,
                ],
                ["", create_paragraph("التوقيع:", arabic_text_style), idx + 4],
            ]
            sign = create_table(
                sign_data,
                [300, 100, 30],
                style_commands=[
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ],
            )

            # Create main table
            table = create_table(
                data,
                [150, 100, 150, 30],
                style_commands=[
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "RIGHT",
                    ),  # Changed to 'RIGHT' alignment
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ],
            )

            elements.extend(
                [title, Spacer(1, 10), date, Spacer(1, 10), table, space, sign],
            )
            doc.build(
                elements,
                onFirstPage=lambda canvas, doc: canvas.setTitle("تحميل من المكتب"),
            )

            return buffer.getvalue()

        # Generate the PDF
        pdf_data = create_document()

        # Save the PDF to the model's FileField
        self.pdf.save("تحميل من المكتب.pdf", io.BytesIO(pdf_data), save=False)

        # Save the model again to ensure the file is linked
        super().save()


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
    from_warehouse_name = models.CharField(max_length=100, blank=True)
    to_warehouse_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"From {self.From} To {self.To}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Capture the warehouse names before any transfer happens
            self.from_warehouse_name = self.From.qr.wh.name
            self.to_warehouse_name = self.To.name

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
