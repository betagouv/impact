# Generated by Django 4.1.5 on 2023-01-24 14:07
import django.db.models.fields
from django.db import migrations

import reglementations.models


class Migration(migrations.Migration):

    dependencies = [
        ("reglementations", "0004_bdese_50_300_completion_steps"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bdese_50_300",
            name="completion_steps",
            field=reglementations.models.CategoryField(
                base_field=django.db.models.fields.BooleanField,
                categories=[
                    "Catégories professionnelles",
                    "Investissement social",
                    "Investissement matériel et immatériel",
                    "Egalité professionnelle homme/femme",
                    "Fonds propres, endettement et impôts",
                    "Rémunérations",
                    "Représentation du personnel et Activités sociales et culturelles",
                    "Rémunération des financeurs",
                    "Flux financiers",
                    "Partenariats",
                    "Transferts commerciaux et financiers",
                    "Environnement",
                ],
                default=reglementations.models.bdese_50_300_completion_steps_default,
            ),
        ),
    ]
