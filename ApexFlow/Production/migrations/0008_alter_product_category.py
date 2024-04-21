# Generated by Django 5.0.4 on 2024-04-20 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Production', '0007_rename_status_product_is_active_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('finished', 'finished'), ('materials', 'materials'), ('services', 'services')], max_length=50, verbose_name='category'),
        ),
    ]
