# Generated by Django 5.0.4 on 2024-04-27 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0006_alter_productunit_item_code_alter_productunit_sku'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productunit',
            name='item_code',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
