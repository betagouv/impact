import html

import pytest
from django.urls import reverse

import api.exceptions
from api.tests.fixtures import mock_api_recherche_entreprises
from entreprises.models import Entreprise
from habilitations.models import attach_entreprise_to_user
from habilitations.models import get_habilitation
from habilitations.models import Habilitation
from habilitations.models import is_user_attached_to_entreprise


def test_entreprises_page_requires_login(client):
    response = client.get("/entreprises")

    assert response.status_code == 302


def test_entreprises_page_for_logged_user(client, alice, entreprise_factory):
    entreprise = entreprise_factory()
    attach_entreprise_to_user(entreprise, alice, "Présidente")
    client.force_login(alice)

    response = client.get("/entreprises")

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "<!-- page entreprises -->" in content


def test_create_and_attach_to_entreprise(client, alice, mock_api_recherche_entreprises):
    client.force_login(alice)
    data = {"siren": "000000001", "fonctions": "Présidente"}

    response = client.post("/entreprises", data=data, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == [(reverse("entreprises:entreprises"), 302)]

    content = html.unescape(response.content.decode("utf-8"))
    assert "L'entreprise a été ajoutée." in content

    entreprise = Entreprise.objects.get(siren="000000001")
    assert get_habilitation(entreprise, alice).fonctions == "Présidente"
    assert entreprise.denomination == "Entreprise SAS"
    assert not entreprise.is_qualified


def test_attach_to_an_existing_entreprise(client, alice, entreprise_factory):
    entreprise = entreprise_factory()
    client.force_login(alice)
    data = {"siren": entreprise.siren, "fonctions": "Présidente"}

    response = client.post("/entreprises", data=data, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == [(reverse("entreprises:entreprises"), 302)]
    assert entreprise in alice.entreprises
    assert get_habilitation(entreprise, alice).fonctions == "Présidente"


def test_fail_to_create_entreprise(client, alice):
    client.force_login(alice)
    data = {"siren": "unvalid", "fonctions": "Présidente"}

    response = client.post("/entreprises", data=data, follow=True)

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    content = html.unescape(response.content.decode("utf-8"))
    assert (
        "Impossible de créer l'entreprise car les données sont incorrectes." in content
    )
    assert Entreprise.objects.count() == 0


def test_fail_to_find_entreprise_in_API(client, alice, mock_api_recherche_entreprises):
    client.force_login(alice)
    mock_api_recherche_entreprises.side_effect = api.exceptions.APIError(
        "L'entreprise n'a pas été trouvée. Vérifiez que le SIREN est correct."
    )
    data = {"siren": "000000001", "fonctions": "Présidente"}

    response = client.post("/entreprises", data=data, follow=True)

    assert response.status_code == 200
    content = html.unescape(response.content.decode("utf-8"))
    assert (
        "L'entreprise n'a pas été trouvée. Vérifiez que le SIREN est correct."
        in content
    )
    assert Entreprise.objects.count() == 0


def test_fail_because_already_existing_habilitation(client, alice, entreprise_factory):
    entreprise = entreprise_factory()
    attach_entreprise_to_user(entreprise, alice, "DG")
    client.force_login(alice)
    data = {"siren": entreprise.siren, "fonctions": "Présidente"}

    response = client.post("/entreprises", data=data, follow=True)

    assert Habilitation.objects.count() == 1
    assert response.status_code == 200
    content = html.unescape(response.content.decode("utf-8"))
    assert (
        "Impossible d'ajouter cette entreprise. Vous y êtes déjà rattaché·e." in content
    )


def test_detach_from_an_entreprise(client, alice, entreprise_factory):
    entreprise = entreprise_factory()
    attach_entreprise_to_user(entreprise, alice, "Présidente")
    client.force_login(alice)

    response = client.delete(f"/entreprises/{entreprise.siren}", follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == [(reverse("entreprises:entreprises"), 302)]
    assert entreprise not in alice.entreprises
    assert not is_user_attached_to_entreprise(alice, entreprise)


def test_qualification_page_is_not_public(client, alice, unqualified_entreprise):
    url = f"/entreprises/{unqualified_entreprise.siren}"
    response = client.get(url)

    assert response.status_code == 302
    connexion_url = reverse("login")
    assert response.url == f"{connexion_url}?next={url}"

    client.force_login(alice)
    response = client.get(url)

    assert response.status_code == 403


def test_qualification_page(
    client, alice, unqualified_entreprise, mock_api_recherche_entreprises
):
    attach_entreprise_to_user(unqualified_entreprise, alice, "Présidente")
    client.force_login(alice)

    response = client.get(f"/entreprises/{unqualified_entreprise.siren}")

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "<!-- page qualification entreprise -->" in content
    mock_api_recherche_entreprises.assert_called_once_with(unqualified_entreprise.siren)

    unqualified_entreprise.refresh_from_db()
    assert unqualified_entreprise.denomination == "Entreprise SAS"
    assert not unqualified_entreprise.is_qualified


def test_qualify_entreprise(
    client, alice, unqualified_entreprise, mock_api_recherche_entreprises
):
    attach_entreprise_to_user(unqualified_entreprise, alice, "Présidente")
    client.force_login(alice)
    data = {
        "effectif": "moyen",
        "bdese_accord": True,
    }

    url = f"/entreprises/{unqualified_entreprise.siren}"
    response = client.get(url)
    response = client.post(url, data=data)

    unqualified_entreprise.refresh_from_db()
    assert unqualified_entreprise.denomination == "Entreprise SAS"
    assert unqualified_entreprise.effectif == "moyen"
    assert unqualified_entreprise.bdese_accord
    assert unqualified_entreprise.is_qualified


def test_qualify_entreprise_error(
    client, alice, unqualified_entreprise, mock_api_recherche_entreprises
):
    attach_entreprise_to_user(unqualified_entreprise, alice, "Présidente")
    client.force_login(alice)
    data = {
        "effectif": "yolo",
        "bdese_accord": True,
    }

    url = f"/entreprises/{unqualified_entreprise.siren}"
    response = client.get(url)
    response = client.post(url, data=data)

    assert response.status_code == 200
    content = html.unescape(response.content.decode("utf-8"))
    assert (
        "L'entreprise n'a pas été enregistrée car le formulaire contient des erreurs"
        in content
    )

    unqualified_entreprise.refresh_from_db()
    assert not unqualified_entreprise.is_qualified
