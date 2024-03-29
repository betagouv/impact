# Generated by Django 4.2.7 on 2023-11-16 16:17
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("metabase", "0009_entreprise_categorie_juridique_sirene"),
    ]

    operations = [
        migrations.AddField(
            model_name="entreprise",
            name="effectif_groupe_permanent",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="entreprise",
            name="effectif_permanent",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="entreprise",
            name="est_cotee",
            field=models.BooleanField(null=True),
        ),
    ]
