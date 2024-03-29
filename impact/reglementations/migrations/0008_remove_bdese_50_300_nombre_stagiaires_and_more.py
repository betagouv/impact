# Generated by Django 4.1.6 on 2023-02-08 15:05
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("reglementations", "0007_bdese_300_created_at_bdese_300_updated_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bdese_50_300",
            name="nombre_stagiaires",
        ),
        migrations.AddField(
            model_name="bdese_300",
            name="evolution_nombre_stagiaires",
            field=models.TextField(
                blank=True, null=True, verbose_name="Évolution du nombre de stagiaires"
            ),
        ),
        migrations.AddField(
            model_name="bdese_50_300",
            name="evolution_nombre_stagiaires",
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name="Évolution du nombre de stagiaires de plus de 16 ans",
            ),
        ),
    ]
