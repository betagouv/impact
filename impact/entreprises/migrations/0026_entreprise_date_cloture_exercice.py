# Generated by Django 4.2.3 on 2023-07-07 13:57
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("entreprises", "0025_caracteristiquesannuelles_systeme_management_energie"),
    ]

    operations = [
        migrations.AddField(
            model_name="entreprise",
            name="date_cloture_exercice",
            field=models.DateField(
                null=True, verbose_name="Date de clôture du dernier exercice comptable"
            ),
        ),
    ]
