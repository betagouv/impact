# Generated by Django 4.1.7 on 2023-03-03 15:13
from django.db import migrations


def transform_official_bdese_into_personal_bdese(apps, schema_editor):
    BDESE_50_300 = apps.get_model("reglementations", "BDESE_50_300")
    for bdese in BDESE_50_300.objects.all():
        try:
            users = bdese.entreprise.users.all()
            bdese.user = users[0]
            bdese.save()
            bdese.pk = None
            bdese._state.adding = True
            for user in users[1:]:
                bdese.user = user
                bdese.save()
        except IndexError:
            print(str(bdese.entreprise))
    BDESE_300 = apps.get_model("reglementations", "BDESE_300")
    for bdese in BDESE_300.objects.all():
        try:
            users = bdese.entreprise.users.all()
            bdese.user = users[0]
            bdese.save()
            bdese.pk = None
            bdese._state.adding = True
            for user in users[1:]:
                bdese.user = user
                bdese.save()
        except IndexError:
            print(str(bdese.entreprise))


class Migration(migrations.Migration):

    dependencies = [
        ("reglementations", "0016_bdese_300_user_bdese_50_300_user"),
    ]

    operations = [
        migrations.RunPython(
            transform_official_bdese_into_personal_bdese,
            reverse_code=migrations.RunPython.noop,
        )
    ]
