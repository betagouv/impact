# Generated by Django 4.1.7 on 2023-03-07 15:04
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("entreprises", "0011_alter_entreprise_users"),
        ("habilitations", "0002_copy_habilitations_data"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Habilitation",
        ),
    ]
