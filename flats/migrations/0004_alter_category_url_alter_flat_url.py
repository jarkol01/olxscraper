# Generated by Django 4.2.2 on 2023-09-24 16:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("flats", "0003_alter_category_options_alter_flat_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="url",
            field=models.CharField(
                help_text="Enter an OLX url with parameters you want to search, price and distance parameters will be overriden if specified. Localization should be replaced with {}. Ex. https://www.olx.pl/elektronika/telefony/smartfony-telefony-komorkowe/{}/?search%5Bfilter_enum_phonemodel%5D%5B0%5D=iphone-14-pro-max&search%5Bfilter_enum_phonemodel%5D%5B1%5D=iphone-14-pro",
                max_length=500,
            ),
        ),
        migrations.AlterField(
            model_name="flat",
            name="url",
            field=models.URLField(max_length=255),
        ),
    ]