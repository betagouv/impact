import json

from django.urls import reverse
import pytest

from reglementations.models import annees_a_remplir_bdese, BDESE_50_300, BDESE_300
from reglementations.tests.test_bdese_forms import categories_form_data
from reglementations.views import get_bdese_data_from_egapro


def test_bdese_is_not_public(client, django_user_model, grande_entreprise):
    url = f"/bdese/{grande_entreprise.siren}/2022/1"
    response = client.get(url)

    assert response.status_code == 302
    connexion_url = reverse("login")
    assert response.url == f"{connexion_url}?next={url}"

    user = django_user_model.objects.create()
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.parametrize(
    "effectif, bdese_class", [("moyen", BDESE_50_300), ("grand", BDESE_300)]
)
def test_yearly_bdese_is_created_at_first_authorized_request(
    effectif, bdese_class, client, django_user_model, entreprise_factory
):
    entreprise = entreprise_factory(effectif=effectif)
    user = django_user_model.objects.create()
    entreprise.users.add(user)
    client.force_login(user)

    assert not bdese_class.objects.filter(entreprise=entreprise)

    url = f"/bdese/{entreprise.siren}/2021/1"
    response = client.get(url)

    assert response.status_code == 302
    bdese_2021 = bdese_class.objects.get(entreprise=entreprise, annee=2021)

    url = f"/bdese/{entreprise.siren}/2022/1"
    response = client.get(url)

    bdese_2022 = bdese_class.objects.get(entreprise=entreprise, annee=2022)
    assert bdese_2021 != bdese_2022


@pytest.fixture
def authorized_user(bdese, django_user_model):
    user = django_user_model.objects.create()
    bdese.entreprise.users.add(user)
    return user


def bdese_step_url(bdese, step):
    return f"/bdese/{bdese.entreprise.siren}/{bdese.annee}/{step}"


def test_bdese_step_redirect_to_categories_professionnelles_if_not_filled(
    bdese, authorized_user, client
):
    client.force_login(authorized_user)

    url = bdese_step_url(bdese, 1)
    response = client.get(url, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == [
        (
            reverse(
                "categories_professionnelles",
                args=[bdese.entreprise.siren, bdese.annee],
            ),
            302,
        )
    ]
    assert (
        "Commencez par renseigner vos cat??gories professionnelles"
        in response.content.decode("utf-8")
    )


def test_bdese_step_use_categories_professionnelles_and_annees_a_remplir(
    bdese, authorized_user, client
):
    categories_professionnelles = ["cat??gorie 1", "cat??gorie 2", "cat??gorie 3"]
    bdese.categories_professionnelles = categories_professionnelles
    bdese.save()
    client.force_login(authorized_user)

    url = bdese_step_url(bdese, 1)
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    for category in categories_professionnelles:
        assert category in content
    for annee in annees_a_remplir_bdese():
        assert str(annee) in content


def test_bdese_step_fetch_data(bdese, authorized_user, client, mocker):
    categories_professionnelles = ["cat??gorie 1", "cat??gorie 2", "cat??gorie 3"]
    bdese.categories_professionnelles = categories_professionnelles
    bdese.save()
    client.force_login(authorized_user)

    fetch_data = mocker.patch("reglementations.views.get_bdese_data_from_egapro")

    url = bdese_step_url(bdese, 1)
    response = client.get(url)

    fetch_data.assert_called_once_with(bdese.entreprise, bdese.annee)


@pytest.fixture
def bdese_300(bdese_factory):
    bdese = bdese_factory(bdese_class=BDESE_300)
    return bdese


@pytest.fixture
def bdese_300_with_categories(bdese_300):
    bdese_300.categories_professionnelles = [
        "cat??gorie 1",
        "cat??gorie 2",
        "cat??gorie 3",
    ]
    bdese_300.categories_professionnelles_detaillees = [
        "cat??gorie d??taill??e 1",
        "cat??gorie d??taill??e 2",
        "cat??gorie d??taill??e 3",
        "cat??gorie d??taill??e 4",
        "cat??gorie d??taill??e 5",
    ]
    bdese_300.mark_step_as_complete(0)
    bdese_300.save()
    return bdese_300


def test_bdese_300_step_use_categories_professionnelles_detaillees(
    bdese_300_with_categories, django_user_model, client
):
    bdese = bdese_300_with_categories
    user = django_user_model.objects.create()
    bdese.entreprise.users.add(user)
    client.force_login(user)

    url = bdese_step_url(bdese, 1)
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    for category in bdese.categories_professionnelles_detaillees:
        assert category in content


def test_save_step_error(bdese_300_with_categories, django_user_model, client):
    bdese = bdese_300_with_categories
    user = django_user_model.objects.create()
    bdese.entreprise.users.add(user)
    client.force_login(user)

    url = bdese_step_url(bdese, 1)
    response = client.post(url, {"unite_absenteisme": "yolo"})

    assert response.status_code == 200
    assert (
        "L&#x27;??tape n&#x27;a pas ??t?? enregistr??e car le formulaire contient des erreurs"
        in response.content.decode("utf-8")
    )

    bdese.refresh_from_db()
    assert bdese.unite_absenteisme != "yolo"


def test_save_step_as_draft_success(
    bdese_300_with_categories, django_user_model, client
):
    bdese = bdese_300_with_categories
    user = django_user_model.objects.create()
    bdese.entreprise.users.add(user)
    client.force_login(user)

    url = bdese_step_url(bdese, 1)
    response = client.post(url, {"unite_absenteisme": "H"})

    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert "??tape enregistr??e" in content
    assert "Enregistrer et marquer comme termin??" in content
    assert "Enregistrer en brouillon" in content

    bdese.refresh_from_db()
    assert bdese.unite_absenteisme == "H"
    assert not bdese.step_is_complete(1)


def test_save_step_and_mark_as_complete_success(
    bdese_300_with_categories, django_user_model, client
):
    bdese = bdese_300_with_categories
    user = django_user_model.objects.create()
    bdese.entreprise.users.add(user)
    client.force_login(user)

    url = bdese_step_url(bdese, 1)
    response = client.post(
        url, {"unite_absenteisme": "H", "save_complete": ""}, follow=True
    )

    assert response.status_code == 200
    assert response.redirect_chain == [(url, 302)]

    content = response.content.decode("utf-8")
    assert "??tape enregistr??e" in content
    assert "Repasser en brouillon pour modifier" in content

    bdese.refresh_from_db()
    assert bdese.unite_absenteisme == "H"
    assert bdese.step_is_complete(1)


def test_mark_step_as_incomplete(bdese_300_with_categories, django_user_model, client):
    bdese = bdese_300_with_categories
    bdese.mark_step_as_complete(1)
    bdese.save()

    bdese.refresh_from_db()
    assert bdese.step_is_complete(1)

    user = django_user_model.objects.create()
    bdese.entreprise.users.add(user)
    client.force_login(user)

    url = bdese_step_url(bdese, 1)
    response = client.post(url, {"mark_incomplete": ""}, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == [(url, 302)]

    content = response.content.decode("utf-8")
    assert "??tape enregistr??e" not in content
    assert "Enregistrer et marquer comme termin??" in content
    assert "Enregistrer en brouillon" in content

    bdese.refresh_from_db()
    assert not bdese.step_is_complete(1)


@pytest.mark.slow
def test_get_pdf(bdese, authorized_user, client):
    client.force_login(authorized_user)

    url = f"/bdese/{bdese.entreprise.siren}/{bdese.annee}/pdf"
    response = client.get(url)

    assert response.status_code == 200


def test_get_categories_professionnelles(bdese, authorized_user, client):
    client.force_login(authorized_user)

    url = bdese_step_url(bdese, 0)
    response = client.get(url)

    assert response.status_code == 200


def test_save_categories_professionnelles(bdese, authorized_user, client):
    client.force_login(authorized_user)

    categories_pro = ["cat??gorie 1", "cat??gorie 2", "cat??gorie 3"]
    categories_pro_detaillees = [
        "cat??gorie d??taill??e 1",
        "cat??gorie d??taill??e 2",
        "cat??gorie d??taill??e 3",
        "cat??gorie d??taill??e 4",
        "cat??gorie d??taill??e 5",
    ]
    data = categories_form_data(categories_pro, categories_pro_detaillees)

    url = bdese_step_url(bdese, 0)
    response = client.post(
        url,
        data=data,
        follow=True,
    )

    assert response.status_code == 200
    if bdese.is_bdese_300:
        next_step_url = url
    else:
        next_step_url = bdese_step_url(bdese, 1)
    assert response.redirect_chain == [(next_step_url, 302)]

    content = response.content.decode("utf-8")
    assert "Cat??gories enregistr??es" in content

    bdese.refresh_from_db()
    assert bdese.categories_professionnelles == categories_pro
    if bdese.is_bdese_300:
        assert bdese.categories_professionnelles_detaillees == categories_pro_detaillees
        assert not bdese.step_is_complete(0)


def test_save_and_complete_categories_professionnelles(
    bdese_300, django_user_model, client
):
    bdese = bdese_300
    user = django_user_model.objects.create()
    bdese.entreprise.users.add(user)
    client.force_login(user)

    categories_pro = ["cat??gorie 1", "cat??gorie 2", "cat??gorie 3"]
    categories_pro_detaillees = [
        "cat??gorie d??taill??e 1",
        "cat??gorie d??taill??e 2",
        "cat??gorie d??taill??e 3",
        "cat??gorie d??taill??e 4",
        "cat??gorie d??taill??e 5",
    ]
    data = categories_form_data(categories_pro, categories_pro_detaillees)
    data.update({"save_complete": ""})

    url = bdese_step_url(bdese, 0)
    response = client.post(
        url,
        data=data,
        follow=True,
    )

    assert response.status_code == 200
    assert response.redirect_chain == [(bdese_step_url(bdese, 1), 302)]

    content = response.content.decode("utf-8")
    assert "Cat??gories enregistr??es" in content

    bdese.refresh_from_db()
    assert bdese.categories_professionnelles == categories_pro
    assert bdese.categories_professionnelles_detaillees == categories_pro_detaillees
    assert bdese.step_is_complete(0)


def test_mark_as_incomplete_categories_professionnelles(
    bdese_300_with_categories, django_user_model, client
):
    bdese = bdese_300_with_categories
    categories_pro = bdese.categories_professionnelles
    categories_pro_detaillees = bdese.categories_professionnelles_detaillees
    user = django_user_model.objects.create()
    bdese.entreprise.users.add(user)
    client.force_login(user)

    url = bdese_step_url(bdese, 0)
    response = client.post(
        url,
        data={"mark_incomplete": ""},
        follow=True,
    )

    assert response.status_code == 200
    assert response.redirect_chain == [(url, 302)]

    content = response.content.decode("utf-8")
    assert "Cat??gories enregistr??es" not in content

    bdese.refresh_from_db()
    assert bdese.categories_professionnelles == categories_pro
    assert bdese.categories_professionnelles_detaillees == categories_pro_detaillees
    assert not bdese.step_is_complete(0)


def test_save_categories_professionnelles_error(bdese, authorized_user, client):
    categories_pro = ["cat??gorie 1", "cat??gorie 2"]
    client.force_login(authorized_user)

    url = bdese_step_url(bdese, 0)
    response = client.post(url, data=categories_form_data(categories_pro))

    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert "Au moins 3 cat??gories sont requises" in content

    bdese.refresh_from_db()
    assert not bdese.categories_professionnelles


def test_save_categories_professionnelles_for_a_new_year(
    bdese, authorized_user, client
):
    categories_pro = ["cat??gorie 1", "cat??gorie 2", "cat??gorie 3"]
    categories_pro_detaillees = [
        "cat??gorie d??taill??e 1",
        "cat??gorie d??taill??e 2",
        "cat??gorie d??taill??e 3",
        "cat??gorie d??taill??e 4",
        "cat??gorie d??taill??e 5",
    ]
    bdese.categories_professionnelles = categories_pro
    if bdese.is_bdese_300:
        bdese.categories_professionnelles_detaillees = categories_pro_detaillees
    bdese.save()
    client.force_login(authorized_user)

    new_year = bdese.annee + 1

    url = f"/bdese/{bdese.entreprise.siren}/{new_year}/0"
    response = client.get(url)

    content = response.content.decode("utf-8")
    for categorie in categories_pro:
        assert categorie in content
    if bdese.is_bdese_300:
        for categorie in categories_pro_detaillees:
            assert categorie in content
        assert "Enregistrer et marquer comme termin??" in content, content
        assert "Enregistrer en brouillon" in content

    new_categories_pro = ["A", "B", "C", "D"]
    new_categories_pro_detaillees = ["E", "F", "G", "H", "I"]
    response = client.post(
        url,
        data=categories_form_data(new_categories_pro, new_categories_pro_detaillees),
        follow=True,
    )

    assert response.status_code == 200
    if bdese.is_bdese_300:
        assert response.redirect_chain == [
            (reverse("bdese", args=[bdese.entreprise.siren, new_year, 0]), 302)
        ]
    else:
        assert response.redirect_chain == [
            (reverse("bdese", args=[bdese.entreprise.siren, new_year, 1]), 302)
        ]

    content = response.content.decode("utf-8")
    assert "Cat??gories enregistr??es" in content

    bdese.refresh_from_db()
    new_bdese = bdese.__class__.objects.get(entreprise=bdese.entreprise, annee=new_year)
    assert bdese.categories_professionnelles == categories_pro
    assert new_bdese.categories_professionnelles == new_categories_pro
    if bdese.is_bdese_300:
        assert bdese.categories_professionnelles_detaillees == categories_pro_detaillees
        assert (
            new_bdese.categories_professionnelles_detaillees
            == new_categories_pro_detaillees
        )


class MockedResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def json(self):
        return json.loads(self.content)


def test_get_bdese_data_from_egapro(grande_entreprise, mocker):
    # Example response from https://egapro.travail.gouv.fr/api/public/declaration/552032534/2021
    index_egapro_data = """{"entreprise":{"siren":"552032534","r\u00e9gion":"\u00cele-de-France","code_naf":"70.10Z","effectif":{"total":867,"tranche":"251:999"},"d\u00e9partement":"Paris","raison_sociale":"DANONE"},"indicateurs":{"promotions":{"non_calculable":null,"note":15,"objectif_de_progression":null},"augmentations_et_promotions":{"non_calculable":null,"note":null,"objectif_de_progression":null},"r\u00e9mun\u00e9rations":{"non_calculable":null,"note":29,"objectif_de_progression":null},"cong\u00e9s_maternit\u00e9":{"non_calculable":null,"note":15,"objectif_de_progression":null},"hautes_r\u00e9mun\u00e9rations":{"non_calculable":null,"note":0,"objectif_de_progression":null,"r\u00e9sultat":1,"population_favorable":"femmes"}},"d\u00e9claration":{"index":79,"ann\u00e9e_indicateurs":2021,"mesures_correctives":null}}"""

    egapro_request = mocker.patch(
        "requests.get", return_value=MockedResponse(index_egapro_data, 200)
    )

    bdese_data_from_egapro = get_bdese_data_from_egapro(grande_entreprise, 2021)

    assert bdese_data_from_egapro == {"nombre_femmes_plus_hautes_remunerations": 9}
    egapro_request.assert_called_once_with(
        f"https://egapro.travail.gouv.fr/api/public/declaration/{grande_entreprise.siren}/2021"
    )
