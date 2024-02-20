# Generated by Django 4.2.3 on 2024-02-20 13:25
from django.db import migrations
from django.db import models

import api.recherche_entreprises


def maj_effectif_0_49(apps, schema_editor):
    """Mise-à-jour des effectifs qui étaient dans la tranche disparue (0-49)

    La tranche a été séparée en deux nouvelles tranches (0-9 et 10-49).
    """
    CaracteristiquesAnnuelles = apps.get_model(
        "entreprises", "CaracteristiquesAnnuelles"
    )
    for caracteristiques in CaracteristiquesAnnuelles.objects.all():
        if (
            caracteristiques.effectif == "0-49"
            or caracteristiques.effectif_permanent == "0-49"
        ):
            effectif = nouvel_effectif(caracteristiques.entreprise)
            if caracteristiques.effectif == "0-49":
                caracteristiques.effectif = effectif
            if caracteristiques.effectif_permanent == "0-49":
                caracteristiques.effectif_permanent = effectif
            print(
                (
                    "MODIFICATION",
                    caracteristiques.entreprise.siren,
                    caracteristiques.entreprise.denomination,
                    caracteristiques.id,
                )
            )
            caracteristiques.save()


def nouvel_effectif(entreprise):
    try:
        infos_entreprise = api.recherche_entreprises.recherche(entreprise.siren)
        if infos_entreprise["effectif"] == "0-9":
            return "0-9"
        else:
            return "10-49"
    except api.exceptions.APIError as e:
        print(f"ERREUR {e}: {entreprise.siren}")
        return "10-49"


class Migration(migrations.Migration):
    dependencies = [
        ("entreprises", "0041_alter_caracteristiquesannuelles_effectif_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="caracteristiquesannuelles",
            name="effectif",
            field=models.CharField(
                choices=[
                    ("", "Sélectionnez une réponse"),
                    ("0-9", "entre 0 et 9 salariés"),
                    ("10-49", "entre 10 et 49 salariés"),
                    ("50-249", "entre 50 et 249 salariés"),
                    ("250-299", "entre 250 et 299 salariés"),
                    ("300-499", "entre 300 et 499 salariés"),
                    ("500-4999", "entre 500 et 4 999 salariés"),
                    ("5000-9999", "entre 5 000 et 9 999 salariés"),
                    ("10000+", "10 000 salariés ou plus"),
                ],
                help_text="Nombre de salariés (notamment CDI, CDD et salariés à temps partiel) de l'entreprise au prorata de leur temps de présence au cours des douze mois précédents (cf. <a href='https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000006177833/#LEGISCTA000006177833' target='_blank' rel='noopener'>articles L.1111-2 et L.1111-3 du Code du Travail</a>)",
                max_length=9,
                null=True,
                verbose_name="Effectif",
            ),
        ),
        migrations.AlterField(
            model_name="caracteristiquesannuelles",
            name="effectif_permanent",
            field=models.CharField(
                choices=[
                    ("", "Sélectionnez une réponse"),
                    ("0-9", "entre 0 et 9 salariés"),
                    ("10-49", "entre 10 et 49 salariés"),
                    ("50-249", "entre 50 et 249 salariés"),
                    ("250-299", "entre 250 et 299 salariés"),
                    ("300-499", "entre 300 et 499 salariés"),
                    ("500-4999", "entre 500 et 4 999 salariés"),
                    ("5000-9999", "entre 5 000 et 9 999 salariés"),
                    ("10000+", "10 000 salariés ou plus"),
                ],
                help_text="Nombre moyen de salariés à temps plein, titulaires d'un contrat à durée indéterminée employés par l'entreprise au cours de l'exercice comptable",
                max_length=9,
                null=True,
                verbose_name="Effectif permanent",
            ),
        ),
        migrations.RunPython(
            maj_effectif_0_49,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
