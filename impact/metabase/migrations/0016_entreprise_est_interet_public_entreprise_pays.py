# Generated by Django 4.2.7 on 2024-03-13 14:41
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("metabase", "0015_entreprise_effectif_groupe_france_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="entreprise",
            name="est_interet_public",
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name="entreprise",
            name="pays",
            field=models.CharField(max_length=50, null=True),
        ),
    ]
