# Generated by Django 5.2.1 on 2025-06-06 12:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alquiler", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="alquiler",
            name="cancelada",
            field=models.BooleanField(default=False),
        ),
    ]
