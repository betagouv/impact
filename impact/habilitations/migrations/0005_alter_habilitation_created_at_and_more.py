# Generated by Django 4.2 on 2023-06-22 14:49
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("habilitations", "0004_habilitation_created_at_habilitation_updated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="habilitation",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="habilitation",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
