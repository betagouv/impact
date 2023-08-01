# Generated by Django 4.2.2 on 2023-06-29 13:33
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("entreprises", "0022_alter_caracteristiquesannuelles_entreprise"),
    ]

    operations = [
        migrations.AddField(
            model_name="caracteristiquesannuelles",
            name="effectif_outre_mer",
            field=models.CharField(
                choices=[
                    ("0-249", "moins de 250 salariés"),
                    ("250+", "250 salariés ou plus"),
                ],
                help_text="Nombre de salariés dans les régions et départements d'outre-mer",
                max_length=9,
                null=True,
                verbose_name="Effectif outre-mer",
            ),
        ),
    ]
