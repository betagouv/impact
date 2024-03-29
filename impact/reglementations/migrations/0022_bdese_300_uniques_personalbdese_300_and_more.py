# Generated by Django 4.2.2 on 2023-06-20 13:46
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("reglementations", "0021_officialbdeseavecaccord_personalbdeseavecaccord"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="bdese_300",
            constraint=models.UniqueConstraint(
                fields=("entreprise", "user", "annee"), name="uniques_PersonalBDESE_300"
            ),
        ),
        migrations.AddConstraint(
            model_name="bdese_300",
            constraint=models.UniqueConstraint(
                condition=models.Q(("user", None)),
                fields=("entreprise", "annee"),
                name="uniques_OfficialBDESE_300",
            ),
        ),
        migrations.AddConstraint(
            model_name="bdese_50_300",
            constraint=models.UniqueConstraint(
                fields=("entreprise", "user", "annee"),
                name="uniques_PersonalBDESE_50_300",
            ),
        ),
        migrations.AddConstraint(
            model_name="bdese_50_300",
            constraint=models.UniqueConstraint(
                condition=models.Q(("user", None)),
                fields=("entreprise", "annee"),
                name="uniques_OfficialBDESE_50_300",
            ),
        ),
        migrations.AddConstraint(
            model_name="bdeseavecaccord",
            constraint=models.UniqueConstraint(
                fields=("entreprise", "user", "annee"),
                name="uniques_PersonalBDESEAvecAccord",
            ),
        ),
        migrations.AddConstraint(
            model_name="bdeseavecaccord",
            constraint=models.UniqueConstraint(
                condition=models.Q(("user", None)),
                fields=("entreprise", "annee"),
                name="uniques_OfficialBDESEAvecAccord",
            ),
        ),
    ]
