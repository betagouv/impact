# Generated by Django 4.2 on 2023-04-19 15:23
from django.db import migrations
from django.db import models


def migrate_entreprise_effectif_data(apps, schema_editor):
    Entreprise = apps.get_model("entreprises", "Entreprise")
    for entreprise in Entreprise.objects.all():
        if entreprise.effectif == "petit":
            entreprise.effectif = "0-49"
        elif entreprise.effectif == "moyen":
            entreprise.effectif = "50-299"
        elif entreprise.effectif == "grand":
            entreprise.effectif = "300-499"
        elif entreprise.effectif == "sup500":
            entreprise.effectif = "500+"
        entreprise.save()


class Migration(migrations.Migration):

    dependencies = [
        ("entreprises", "0015_rename_raison_sociale_entreprise_denomination"),
    ]

    operations = [
        migrations.RunPython(
            migrate_entreprise_effectif_data,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="entreprise",
            name="effectif",
            field=models.CharField(
                choices=[
                    ("0-49", "moins de 50 salariés"),
                    ("50-299", "entre 50 et 299 salariés"),
                    ("300-499", "entre 300 et 499 salariés"),
                    ("500+", "500 salariés ou plus"),
                ],
                help_text="Vérifiez et confirmez le nombre de salariés",
                max_length=9,
                null=True,
            ),
        ),
    ]
