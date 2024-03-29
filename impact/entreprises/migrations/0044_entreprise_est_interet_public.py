# Generated by Django 4.2.10 on 2024-03-07 14:44
from django.db import migrations
from django.db import models


def maj_interet_public(apps, schema_editor):
    """Mise-à-jour de l'interet public d'une entreprise
    Une entreprise cotée est forcément d'intérêt public.

    L'intérêt public étant introduit avec la CSRD, certaines entreprises
    étaient déjà renseignées comme cotée mais sont par défaut sans intérêt
    public.
    La migration corrige cet état.
    """
    Entreprises = apps.get_model("entreprises", "Entreprise")
    for entreprise in Entreprises.objects.all():
        if entreprise.est_cotee:
            entreprise.est_interet_public = True
            entreprise.save()
            print(f"Intérêt public pour {entreprise}")
        else:
            print(f"Non cotée : {entreprise}")


class Migration(migrations.Migration):

    dependencies = [
        (
            "entreprises",
            "0043_alter_caracteristiquesannuelles_tranche_bilan_consolide_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="entreprise",
            name="est_interet_public",
            field=models.BooleanField(
                help_text="Entreprises cotées, établissements de crédit, entreprises d'assurance, mutuelles et unions, institutions de prévoyance et unions, organismes de liquidation (cf. <a href='https://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=OJ:L:2013:182:0019:0076:FR:PDF' target='_blank' rel='noopener'>article 2 directive comptable du 26 juin 2013</a>)",
                null=True,
                verbose_name="L'entreprise est d'intérêt public",
            ),
        ),
        migrations.RunPython(
            maj_interet_public,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
