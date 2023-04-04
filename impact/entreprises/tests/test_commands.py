import pytest
from django.core.management import call_command

import api.exceptions
from entreprises.management.commands.force_denomination import Command
from entreprises.models import Entreprise as Entreprise


@pytest.mark.django_db(transaction=True)
def test_remplit_la_denomination(db, mocker, unqualified_entreprise):
    unqualified_entreprise.denomination = ""
    unqualified_entreprise.save()
    RAISON_SOCIALE = "RAISON SOCIALE"

    mocker.patch(
        "api.recherche_entreprises.recherche",
        return_value={
            "siren": unqualified_entreprise.siren,
            "effectif": "moyen",
            "denomination": RAISON_SOCIALE,
        },
    )
    Command().handle()

    unqualified_entreprise.refresh_from_db()
    assert unqualified_entreprise.denomination == RAISON_SOCIALE


@pytest.mark.django_db(transaction=True)
def test_ne_modifie_pas_la_denomination_si_deja_remplie(
    db, mocker, unqualified_entreprise
):
    RAISON_SOCIALE = unqualified_entreprise.denomination

    mocker.patch(
        "api.recherche_entreprises.recherche",
        return_value={
            "siren": unqualified_entreprise.siren,
            "effectif": "moyen",
            "denomination": "RAISON SOCIALE",
        },
    )
    Command().handle()

    unqualified_entreprise.refresh_from_db()
    assert unqualified_entreprise.denomination == RAISON_SOCIALE


@pytest.mark.django_db(transaction=True)
def test_erreur_de_l_api(capsys, db, mocker, unqualified_entreprise):
    unqualified_entreprise.denomination = ""
    unqualified_entreprise.save()

    mocker.patch(
        "api.recherche_entreprises.recherche", side_effect=api.exceptions.APIError
    )
    call_command("force_denomination")

    assert unqualified_entreprise.denomination == ""
    captured = capsys.readouterr()
    assert captured.out.startswith("ERREUR")
    assert captured.out.endswith(f"{unqualified_entreprise.siren}\n")
