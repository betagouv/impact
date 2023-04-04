import pytest
from django.urls import reverse

from entreprises.models import Entreprise as ImpactEntreprise
from impact.settings import METABASE_DATABASE_NAME
from metabase.management.commands.sync_metabase import Command
from metabase.models import Entreprise as MetabaseEntreprise


@pytest.mark.django_db(transaction=True, databases=["default", METABASE_DATABASE_NAME])
def test_synchronise_metabase_once():
    entreprise_A = ImpactEntreprise.objects.create(
        siren="000000001",
        effectif="petit",
        bdese_accord=True,
        denomination="A",
    )
    entreprise_A.effectif = "grand"
    entreprise_A.save()

    Command().handle()

    metabase_entreprise = MetabaseEntreprise.objects.all()[0]
    assert metabase_entreprise.denomination == "A"
    assert metabase_entreprise.siren == "000000001"
    assert metabase_entreprise.effectif == "grand"
    assert metabase_entreprise.bdese_accord == True
    assert metabase_entreprise.created_at == entreprise_A.created_at
    assert metabase_entreprise.updated_at == entreprise_A.updated_at


@pytest.mark.django_db(transaction=True, databases=["default", METABASE_DATABASE_NAME])
def test_synchronise_several_times():
    ImpactEntreprise.objects.create(
        siren="000000001",
        effectif="petit",
        bdese_accord=True,
        denomination="A",
    )

    Command().handle()
    Command().handle()

    metabase_entreprise = MetabaseEntreprise.objects.all()[0]
    assert metabase_entreprise.denomination == "A"
    assert metabase_entreprise.siren == "000000001"
    assert metabase_entreprise.effectif == "petit"
    assert metabase_entreprise.bdese_accord == True
