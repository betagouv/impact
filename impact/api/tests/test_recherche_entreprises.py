import pytest
from requests.exceptions import Timeout

from api.exceptions import APIError
from api.exceptions import ServerError
from api.exceptions import SirenError
from api.exceptions import TooManyRequestError
from api.recherche_entreprises import recherche
from api.recherche_entreprises import RECHERCHE_ENTREPRISE_TIMEOUT
from entreprises.models import CaracteristiquesAnnuelles


@pytest.mark.network
def test_api_fonctionnelle():
    SIREN = "130025265"
    infos = recherche(SIREN)

    assert infos == {
        "siren": SIREN,
        "effectif": CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249,
        "denomination": "DIRECTION INTERMINISTERIELLE DU NUMERIQUE",
        "categorie_juridique_sirene": 7120,
        "code_pays_etranger_sirene": None,
    }


def test_succes_recherche_comportant_la_raison_sociale(mocker):
    SIREN = "123456789"

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "total_results": 1,
                "results": [
                    {
                        "nom_complet": "entreprise",
                        "nom_raison_sociale": "ENTREPRISE",
                        "tranche_effectif_salarie": "12",
                        "nature_juridique": "5710",
                        "siege": {"code_pays_etranger": "99139"},
                    }
                ],
            }

    faked_request = mocker.patch("requests.get", return_value=FakeResponse())

    infos = recherche(SIREN)

    assert infos == {
        "siren": SIREN,
        "effectif": CaracteristiquesAnnuelles.EFFECTIF_ENTRE_10_ET_49,
        "denomination": "ENTREPRISE",
        "categorie_juridique_sirene": 5710,
        "code_pays_etranger_sirene": 99139,
    }
    faked_request.assert_called_once_with(
        f"https://recherche-entreprises.api.gouv.fr/search?q={SIREN}&page=1&per_page=1",
        timeout=RECHERCHE_ENTREPRISE_TIMEOUT,
    )


def test_succes_recherche_sans_la_raison_sociale(mocker):
    SIREN = "123456789"

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "total_results": 1,
                "results": [
                    {
                        "nom_complet": "ENTREPRISE",
                        "nom_raison_sociale": None,
                        "tranche_effectif_salarie": "12",
                        "nature_juridique": "5710",
                        "siege": {"code_pays_etranger": None},
                    }
                ],
            }

    mocker.patch("requests.get", return_value=FakeResponse())
    infos = recherche(SIREN)

    assert infos == {
        "siren": SIREN,
        "effectif": CaracteristiquesAnnuelles.EFFECTIF_ENTRE_10_ET_49,
        "denomination": "ENTREPRISE",
        "categorie_juridique_sirene": 5710,
        "code_pays_etranger_sirene": None,
    }


def test_succes_pas_de_resultat(mocker):
    SIREN = "123456789"

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "results": [],
                "total_results": 0,
                "page": 1,
                "per_page": 1,
                "total_pages": 0,
            }

    mocker.patch("requests.get", return_value=FakeResponse())
    with pytest.raises(SirenError) as e:
        recherche(SIREN)

    assert (
        str(e.value)
        == "L'entreprise n'a pas été trouvée. Vérifiez que le SIREN est correct."
    )


def test_echec_recherche_requete_api_invalide(mocker):
    SIREN = "123456789"

    class FakeResponse:
        status_code = 400

    mocker.patch("requests.get", return_value=FakeResponse())
    capture_message_mock = mocker.patch("sentry_sdk.capture_message")
    with pytest.raises(APIError) as e:
        recherche(SIREN)

    capture_message_mock.assert_called_once_with(
        "Requête invalide sur l'API recherche entreprise"
    )
    assert (
        str(e.value)
        == "Le service est actuellement indisponible. Merci de réessayer plus tard."
    )


def test_echec_trop_de_requetes(mocker):
    SIREN = "123456789"

    class FakeResponse:
        status_code = 429

    mocker.patch("requests.get", return_value=FakeResponse())
    with pytest.raises(TooManyRequestError) as e:
        recherche(SIREN)

    assert (
        str(e.value) == "Le service est temporairement surchargé. Merci de réessayer."
    )


def test_echec_erreur_de_l_API(mocker):
    SIREN = "123456789"

    class FakeResponse:
        status_code = 500

    mocker.patch("requests.get", return_value=FakeResponse())
    capture_message_mock = mocker.patch("sentry_sdk.capture_message")

    with pytest.raises(ServerError) as e:
        recherche(SIREN)

    capture_message_mock.assert_called_once_with("Erreur API recherche entreprise")
    assert (
        str(e.value)
        == "Le service est actuellement indisponible. Merci de réessayer plus tard."
    )


def test_echec_exception_provoquee_par_l_api(mocker):
    """le Timeout est un cas réel mais l'implémentation attrape toutes les erreurs possibles"""
    SIREN = "123456789"

    faked_request = mocker.patch("requests.get", side_effect=Timeout)
    capture_exception_mock = mocker.patch("sentry_sdk.capture_exception")

    with pytest.raises(APIError) as e:
        recherche(SIREN)

    capture_exception_mock.assert_called_once()
    args, _ = capture_exception_mock.call_args
    assert type(args[0]) == Timeout
    assert (
        str(e.value)
        == "Le service est actuellement indisponible. Merci de réessayer plus tard."
    )


def test_entreprise_inexistante_mais_pourtant_retournée_par_l_API(mocker):
    # Le SIREN ne correspond pas à une entreprise réelle mais l'API répond
    # comme si l'entreprise existait. Actuellement, le seul cas connu est le siren 0000000000.
    # On souhaite être informé si ce n'est pas le cas car d'autres cas similaires pourrait être retournés.
    SIREN = "000000000"

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "total_results": 1,
                "results": [
                    {
                        "nom_complet": None,
                        "nom_raison_sociale": None,
                        "tranche_effectif_salarie": "15",
                        "nature_juridique": None,
                        "nombre_etablissements": 0,
                        "nombre_etablissements_ouverts": 0,
                        "siege": {},
                        "activite_principale": None,
                    }
                ],
            }

    mocker.patch("requests.get", return_value=FakeResponse())
    capture_message_mock = mocker.patch("sentry_sdk.capture_message")

    with pytest.raises(SirenError) as e:
        recherche(SIREN)

    assert str(e.value) == "Aucune entreprise ne correspond à ce SIREN."
    capture_message_mock.assert_called_once_with(
        "Entreprise inexistante mais retournée par l'API recherche entreprise"
    )


@pytest.mark.parametrize("nature_juridique", ["", None])
def test_pas_de_nature_juridique(nature_juridique, mocker):
    # On se sert de la catégorie juridique pour certaines réglementations qu'on récupère via la nature juridique renvoyée par l'API.
    # Normalement toutes les entreprises en ont une.
    # On souhaite être informé si ce n'est pas le cas car le diagnostic pour ces réglementations pourrait être faux.
    SIREN = "123456789"

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "total_results": 1,
                "results": [
                    {
                        "nom_complet": "ENTREPRISE",
                        "nom_raison_sociale": None,
                        "tranche_effectif_salarie": "15",
                        "nature_juridique": nature_juridique,
                        "siege": {"code_pays_etranger": None},
                    }
                ],
            }

    mocker.patch("requests.get", return_value=FakeResponse())
    capture_message_mock = mocker.patch("sentry_sdk.capture_message")

    infos = recherche(SIREN)

    capture_message_mock.assert_called_once_with(
        "Nature juridique récupérée par l'API recherche entreprise invalide"
    )
    assert infos["categorie_juridique_sirene"] == None


def test_pas_de_code_pays_etranger(mocker):
    # On souhaite être informé s'il est manquant (utilisé dans la réglementation CSRD).
    SIREN = "123456789"

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "total_results": 1,
                "results": [
                    {
                        "nom_complet": "ENTREPRISE",
                        "nom_raison_sociale": None,
                        "tranche_effectif_salarie": "15",
                        "nature_juridique": "5710",
                        "siege": {},
                    }
                ],
            }

    mocker.patch("requests.get", return_value=FakeResponse())
    capture_message_mock = mocker.patch("sentry_sdk.capture_message")

    infos = recherche(SIREN)

    capture_message_mock.assert_called_once_with(
        "Code pays étranger récupéré par l'API recherche entreprise invalide"
    )
    assert infos["code_pays_etranger_sirene"] == None


def test_code_pays_etranger_vaut_null_car_en_France(mocker):
    SIREN = "123456789"

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "total_results": 1,
                "results": [
                    {
                        "nom_complet": "ENTREPRISE",
                        "nom_raison_sociale": None,
                        "tranche_effectif_salarie": "15",
                        "nature_juridique": "5710",
                        "siege": {"code_pays_etranger": None},
                    }
                ],
            }

    mocker.patch("requests.get", return_value=FakeResponse())
    capture_message_mock = mocker.patch("sentry_sdk.capture_message")

    infos = recherche(SIREN)

    assert not capture_message_mock.called
    assert infos["code_pays_etranger_sirene"] == None
