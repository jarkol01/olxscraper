# Generated by Django 4.2.2 on 2023-07-06 19:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("flats", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="search",
            field=models.BooleanField(default=True),
        ),
    ]
