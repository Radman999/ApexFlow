# Generated by Django 5.0.4 on 2024-04-27 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0002_alter_qr_productunit_remove_productunit_unit_frac_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productunit',
            name='picture',
            field=models.URLField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='productunit',
            name='related_item_code',
            field=models.JSONField(blank=True, default=[]),
        ),
    ]
