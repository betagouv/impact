# Generated by Django 4.2.3 on 2024-02-23 13:55
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("entreprises", "0042_alter_caracteristiquesannuelles_effectif_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="caracteristiquesannuelles",
            name="tranche_bilan_consolide",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Sélectionnez une réponse"),
                    ("0-20M", "entre 0 et 20M€"),
                    ("20M-30M", "entre 20M€ et 30M€"),
                    ("30M-43M", "entre 30M€ et 43M€"),
                    ("43M-100M", "entre 43M€ et 100M€"),
                    ("100M+", "100M€ ou plus"),
                ],
                max_length=9,
                null=True,
                verbose_name="Bilan consolidé du groupe",
            ),
        ),
        migrations.AlterField(
            model_name="caracteristiquesannuelles",
            name="tranche_chiffre_affaires_consolide",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Sélectionnez une réponse"),
                    ("0-40M", "entre 0 et 40M€"),
                    ("40-60M", "entre 40M€ et 60M€"),
                    ("60-100M", "entre 60M€ et 100M€"),
                    ("100M+", "100M€ ou plus"),
                ],
                max_length=9,
                null=True,
                verbose_name="Chiffre d'affaires consolidé du groupe",
            ),
        ),
    ]
