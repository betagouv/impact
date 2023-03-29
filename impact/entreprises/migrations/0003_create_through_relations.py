# Generated by Django 4.1.4 on 2023-01-10 09:48
from django.db import migrations


def create_through_relations(apps, schema_editor):
    Entreprise = apps.get_model("entreprises", "Entreprise")
    Habilitation = apps.get_model("entreprises", "Habilitation")
    for entreprise in Entreprise.objects.all():
        for user in entreprise.users.all():
            Habilitation(
                user=user,
                entreprise=entreprise,
            ).save()


class Migration(migrations.Migration):

    dependencies = [
        ("entreprises", "0002_habilitation"),
    ]

    operations = [
        migrations.RunPython(
            create_through_relations,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
