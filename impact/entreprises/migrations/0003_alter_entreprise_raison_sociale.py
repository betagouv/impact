# Generated by Django 4.1.2 on 2022-12-06 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("entreprises", "0002_alter_entreprise_effectif"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entreprise",
            name="raison_sociale",
            field=models.CharField(default="", max_length=250),
        ),
    ]
