# Generated by Django 4.1.7 on 2023-03-28 07:56
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("metabase", "0002_alter_entreprise_created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entreprise",
            name="effectif",
            field=models.CharField(max_length=9, null=True),
        ),
    ]
