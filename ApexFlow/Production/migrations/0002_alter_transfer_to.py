# Generated by Django 5.0.4 on 2024-04-17 13:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Production', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transfer',
            name='To',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_to', to='Production.wh'),
        ),
    ]
