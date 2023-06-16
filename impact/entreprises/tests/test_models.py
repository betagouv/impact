from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest
from django.db import IntegrityError
from freezegun import freeze_time

from entreprises.models import CaracteristiquesAnnuelles
from entreprises.models import Entreprise


@pytest.mark.django_db(transaction=True)
def test_entreprise():
    now = datetime(2023, 1, 27, 16, 1, tzinfo=timezone.utc)

    with freeze_time(now):
        entreprise = Entreprise.objects.create(
            siren="123456789", denomination="Entreprise SAS"
        )

    assert entreprise.created_at == now
    assert entreprise.updated_at == now
    assert entreprise.siren == "123456789"
    assert entreprise.denomination == "Entreprise SAS"
    assert not entreprise.users.all()
    assert not entreprise.is_qualified

    with pytest.raises(IntegrityError):
        Entreprise.objects.create(
            siren="123456789", denomination="Autre Entreprise SAS"
        )

    with freeze_time(now + timedelta(1)):
        entreprise.denomination = "Nouveau nom SAS"
        entreprise.save()

    assert entreprise.updated_at == now + timedelta(1)


@pytest.mark.django_db(transaction=True)
def test_entreprise_is_qualified(unqualified_entreprise):
    assert not unqualified_entreprise.is_qualified

    caracteristiques = unqualified_entreprise.actualise_caracteristiques(
        effectif=CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_50,
        bdese_accord=True,
    )
    caracteristiques.save()

    assert unqualified_entreprise.is_qualified


def test_get_and_actualise_caracteristiques(unqualified_entreprise):
    assert unqualified_entreprise.caracteristiques_actuelles() is None

    effectif = CaracteristiquesAnnuelles.EFFECTIF_ENTRE_300_ET_499
    bdese_accord = False

    caracteristiques = unqualified_entreprise.actualise_caracteristiques(
        effectif, bdese_accord
    )
    caracteristiques.save()

    assert caracteristiques.effectif == effectif
    assert caracteristiques.bdese_accord == bdese_accord
    unqualified_entreprise.refresh_from_db()
    assert unqualified_entreprise.caracteristiques_actuelles() == caracteristiques

    effectif_corrige = CaracteristiquesAnnuelles.EFFECTIF_500_ET_PLUS
    bdese_accord_corrige = True

    caracteristiques_corrigee = unqualified_entreprise.actualise_caracteristiques(
        effectif_corrige, bdese_accord_corrige
    )
    caracteristiques_corrigee.save()

    assert caracteristiques_corrigee.effectif == effectif_corrige
    assert caracteristiques_corrigee.bdese_accord == bdese_accord_corrige
    unqualified_entreprise.refresh_from_db()
    assert (
        unqualified_entreprise.caracteristiques_actuelles() == caracteristiques_corrigee
    )


@pytest.mark.django_db(transaction=True)
def test_caracteristiques_annuelles(unqualified_entreprise):
    with pytest.raises(IntegrityError):
        CaracteristiquesAnnuelles.objects.create(annee=2023)

    CaracteristiquesAnnuelles.objects.create(
        entreprise=unqualified_entreprise, annee=2023
    )


def test_uniques_caracteristiques_annuelles(unqualified_entreprise):
    caracteristiques = CaracteristiquesAnnuelles(
        entreprise=unqualified_entreprise, annee=2023
    )
    caracteristiques.save()

    with pytest.raises(IntegrityError):
        caracteristiques_bis = CaracteristiquesAnnuelles(
            entreprise=unqualified_entreprise, annee=2023
        )
        caracteristiques_bis.save()
