# Generated by Django 4.2.6 on 2023-11-24 15:23
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("entreprises", "0037_entreprise_est_cotee"),
    ]

    operations = [
        migrations.AlterField(
            model_name="caracteristiquesannuelles",
            name="effectif",
            field=models.CharField(
                choices=[
                    ("", "Sélectionnez une réponse"),
                    ("0-49", "moins de 50 salariés"),
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
            name="effectif_groupe",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Sélectionnez une réponse"),
                    ("0-49", "moins de 50 salariés"),
                    ("50-249", "entre 50 et 249 salariés"),
                    ("250-499", "entre 250 et 499 salariés"),
                    ("500-4999", "entre 500 et 4 999 salariés"),
                    ("5000-9999", "entre 5 000 et 9 999 salariés"),
                    ("10000+", "10 000 salariés ou plus"),
                ],
                help_text="Nombre de salariés (notamment CDI, CDD et salariés à temps partiel) du groupe au prorata de leur temps de présence au cours des douze mois précédents (cf. <a href='https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000006177833/#LEGISCTA000006177833' target='_blank' rel='noopener'>articles L.1111-2 et L.1111-3 du Code du Travail</a>)",
                max_length=9,
                null=True,
                verbose_name="Effectif du groupe",
            ),
        ),
        migrations.AlterField(
            model_name="caracteristiquesannuelles",
            name="effectif_outre_mer",
            field=models.CharField(
                choices=[
                    ("", "Sélectionnez une réponse"),
                    ("0-249", "moins de 250 salariés"),
                    ("250+", "250 salariés ou plus"),
                ],
                help_text="Nombre de salariés de l'entreprise dans les régions et départements d'outre-mer au prorata de leur temps de présence au cours des douze mois précédents",
                max_length=9,
                null=True,
                verbose_name="Effectif outre-mer",
            ),
        ),
    ]
