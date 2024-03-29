# Generated by Django 4.1.7 on 2023-04-04 16:00
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reglementations", "0020_bdeseavecaccord"),
    ]

    operations = [
        migrations.CreateModel(
            name="OfficialBDESEAvecAccord",
            fields=[],
            options={
                "verbose_name": "BDESE officielle avec accord d'entreprise",
                "verbose_name_plural": "BDESE officielles avec accord d'entreprise",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("reglementations.bdeseavecaccord",),
        ),
        migrations.CreateModel(
            name="PersonalBDESEAvecAccord",
            fields=[],
            options={
                "verbose_name": "BDESE personnelle avec accord d'entreprise",
                "verbose_name_plural": "BDESE personnelles avec accord d'entreprise",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("reglementations.bdeseavecaccord",),
        ),
    ]
