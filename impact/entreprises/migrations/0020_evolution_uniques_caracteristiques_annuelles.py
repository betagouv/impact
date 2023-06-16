# Generated by Django 4.2 on 2023-06-16 09:16
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("entreprises", "0019_evolution_created_at_evolution_updated_at"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="evolution",
            constraint=models.UniqueConstraint(
                fields=("entreprise", "annee"),
                name="uniques_caracteristiques_annuelles",
            ),
        ),
    ]