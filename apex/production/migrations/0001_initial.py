# Generated by Django 5.0.4 on 2024-08-04 12:04

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('is_active', models.BooleanField(default=False, verbose_name='Status')),
                ('category', models.CharField(choices=[('finished', 'finished'), ('materials', 'materials'), ('services', 'services')], max_length=50, verbose_name='category')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
            },
        ),
        migrations.CreateModel(
            name='ProductUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tenant', models.IntegerField(blank=True, null=True)),
                ('product_name', models.CharField(blank=True, default='', max_length=255)),
                ('product_unit_name', models.CharField(blank=True, default='', max_length=255)),
                ('unit_name', models.CharField(blank=True, default='', max_length=100)),
                ('remaining_quantity', models.IntegerField(blank=True, null=True)),
                ('relative_remaining_quantity', models.IntegerField(blank=True, null=True)),
                ('tier_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created', models.DateTimeField(blank=True)),
                ('modified', models.DateTimeField(blank=True)),
                ('picture', models.URLField(blank=True, default='', null=True)),
                ('sku', models.CharField(blank=True, default='', null=True)),
                ('unit_fraction', models.BigIntegerField(blank=True, null=True)),
                ('old_cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('is_active', models.BooleanField(blank=True, null=True)),
                ('default', models.BooleanField(blank=True, null=True)),
                ('sync_quantity_salla', models.BooleanField(blank=True, null=True)),
                ('quantity_salla', models.BigIntegerField(blank=True, null=True)),
                ('auto_add', models.BooleanField(blank=True, null=True)),
                ('item_code', models.CharField(blank=True, default='', max_length=10)),
                ('related_item_code', models.JSONField(blank=True, default=dict, null=True)),
                ('product', models.IntegerField(blank=True, null=True)),
                ('unit', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='pdfs/')),
                ('is_sent', models.BooleanField(default=False)),
                ('picture', models.FileField(blank=True, null=True, upload_to='pdfs/')),
            ],
        ),
        migrations.CreateModel(
            name='Wh',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('Smacc_Code', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='WhType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'unit',
                'verbose_name_plural': 'units',
            },
        ),
        migrations.CreateModel(
            name='Qr',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('productunit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='production.productunit')),
                ('wh', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wh', to='production.wh')),
            ],
        ),
        migrations.CreateModel(
            name='Zpl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zpl_code', models.TextField()),
                ('random_id', models.IntegerField(default=0, editable=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('qr', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='zpls', to='production.qr')),
            ],
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_warehouse_name', models.CharField(blank=True, max_length=100)),
                ('to_warehouse_name', models.CharField(blank=True, max_length=100)),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to='production.track')),
                ('To', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_to', to='production.wh')),
                ('From', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_from', to='production.zpl')),
            ],
        ),
    ]
