# Generated by Django 4.2.2 on 2023-06-20 23:16

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Flat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("url", models.URLField(max_length=150)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "type",
                    models.CharField(
                        choices=[("P", "Pokoj"), ("M", "Mieszkanie")], max_length=20
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
