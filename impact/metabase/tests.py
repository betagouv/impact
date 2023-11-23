from datetime import date
from datetime import datetime
from datetime import timezone

import pytest
from freezegun import freeze_time

from entreprises.models import ActualisationCaracteristiquesAnnuelles
from entreprises.models import CaracteristiquesAnnuelles
from entreprises.models import Entreprise
from habilitations.models import attach_user_to_entreprise
from impact.settings import METABASE_DATABASE_NAME
from metabase.management.commands.sync_metabase import Command
from metabase.models import BDESE as MetabaseBDESE
from metabase.models import Entreprise as MetabaseEntreprise
from metabase.models import Habilitation as MetabaseHabilitation
from metabase.models import Utilisateur as MetabaseUtilisateur
from reglementations.models import BDESE_50_300
from reglementations.models import derniere_annee_a_remplir_bdese
from reglementations.tests.conftest import bdese_factory  # noqa


@pytest.mark.django_db(transaction=True, databases=["default", METABASE_DATABASE_NAME])
def test_synchronise_une_entreprise_qualifiee_sans_groupe(
    entreprise_factory, date_cloture_dernier_exercice
):
    date_creation = datetime(
        date_cloture_dernier_exercice.year,
        date_cloture_dernier_exercice.month,
        date_cloture_dernier_exercice.day,
        tzinfo=timezone.utc,
    )
    date_deuxieme_evolution = datetime(
        date_cloture_dernier_exercice.year + 1,
        date_cloture_dernier_exercice.month,
        date_cloture_dernier_exercice.day,
        tzinfo=timezone.utc,
    )
    date_troisieme_evolution = datetime(
        date_cloture_dernier_exercice.year + 2,
        date_cloture_dernier_exercice.month,
        date_cloture_dernier_exercice.day,
        tzinfo=timezone.utc,
    )
    date_derniere_qualification = date(
        date_cloture_dernier_exercice.year,
        month=12,
        day=15,
    )
    with freeze_time(date_creation) as frozen_datetime:
        entreprise = entreprise_factory(
            siren="000000001",
            denomination="Entreprise A",
            date_cloture_exercice=date_cloture_dernier_exercice,
            date_derniere_qualification=date_derniere_qualification,
            categorie_juridique_sirene=5699,
            effectif=CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_50,
            effectif_permanent=CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_50,
            effectif_outre_mer=CaracteristiquesAnnuelles.EFFECTIF_OUTRE_MER_MOINS_DE_250,
            est_cotee=False,
            tranche_chiffre_affaires=CaracteristiquesAnnuelles.CA_MOINS_DE_700K,
            tranche_bilan=CaracteristiquesAnnuelles.BILAN_MOINS_DE_350K,
            bdese_accord=False,
            systeme_management_energie=False,
        )
        frozen_datetime.move_to(date_deuxieme_evolution)
        actualisation = ActualisationCaracteristiquesAnnuelles(
            date_cloture_exercice=date_cloture_dernier_exercice.replace(
                year=date_cloture_dernier_exercice.year + 1
            ),
            effectif=CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249,
            effectif_permanent=CaracteristiquesAnnuelles.EFFECTIF_ENTRE_250_ET_299,
            effectif_outre_mer=CaracteristiquesAnnuelles.EFFECTIF_OUTRE_MER_MOINS_DE_250,
            effectif_groupe=None,
            effectif_groupe_permanent=None,
            tranche_chiffre_affaires=CaracteristiquesAnnuelles.CA_ENTRE_700K_ET_12M,
            tranche_bilan=CaracteristiquesAnnuelles.BILAN_ENTRE_350K_ET_6M,
            tranche_chiffre_affaires_consolide=None,
            tranche_bilan_consolide=None,
            bdese_accord=True,
            systeme_management_energie=False,
        )
        entreprise.actualise_caracteristiques(actualisation).save()
        frozen_datetime.move_to(date_troisieme_evolution)
        actualisation = ActualisationCaracteristiquesAnnuelles(
            date_cloture_exercice=date_cloture_dernier_exercice.replace(
                year=date_cloture_dernier_exercice.year + 2
            ),
            effectif=CaracteristiquesAnnuelles.EFFECTIF_ENTRE_300_ET_499,
            effectif_permanent=CaracteristiquesAnnuelles.EFFECTIF_ENTRE_250_ET_299,
            effectif_outre_mer=CaracteristiquesAnnuelles.EFFECTIF_OUTRE_MER_MOINS_DE_250,
            effectif_groupe=None,
            effectif_groupe_permanent=None,
            tranche_chiffre_affaires=CaracteristiquesAnnuelles.CA_ENTRE_12M_ET_40M,
            tranche_bilan=CaracteristiquesAnnuelles.BILAN_ENTRE_6M_ET_20M,
            tranche_chiffre_affaires_consolide=None,
            tranche_bilan_consolide=None,
            bdese_accord=True,
            systeme_management_energie=True,
        )
        entreprise.actualise_caracteristiques(actualisation).save()

    Command().handle()

    assert MetabaseEntreprise.objects.count() == 1
    metabase_entreprise = MetabaseEntreprise.objects.first()
    assert metabase_entreprise.pk == metabase_entreprise.impact_id == entreprise.pk
    assert metabase_entreprise.ajoutee_le == date_creation
    assert metabase_entreprise.modifiee_le == date_troisieme_evolution
    assert metabase_entreprise.siren == "000000001"
    assert metabase_entreprise.denomination == "Entreprise A"
    assert metabase_entreprise.categorie_juridique == "SOCIETE_ANONYME"
    assert (
        metabase_entreprise.date_cloture_exercice
        == date_cloture_dernier_exercice.replace(
            year=date_cloture_dernier_exercice.year + 2
        )
    )
    assert (
        metabase_entreprise.date_derniere_qualification == date_derniere_qualification
    )
    assert metabase_entreprise.est_cotee is False
    assert metabase_entreprise.appartient_groupe is False
    assert metabase_entreprise.societe_mere_en_france is False
    assert metabase_entreprise.comptes_consolides is False
    assert metabase_entreprise.effectif == "300-499"
    assert metabase_entreprise.effectif_permanent == "250-299"
    assert metabase_entreprise.effectif_outre_mer == "0-249"
    assert metabase_entreprise.effectif_groupe is None
    assert metabase_entreprise.tranche_bilan == "6M-20M"
    assert metabase_entreprise.tranche_chiffre_affaires == "12M-40M"
    assert metabase_entreprise.tranche_bilan_consolide is None
    assert metabase_entreprise.tranche_chiffre_affaires_consolide is None
    assert metabase_entreprise.bdese_accord is True
    assert metabase_entreprise.systeme_management_energie is True
    assert metabase_entreprise.nombre_utilisateurs == 0


@pytest.mark.django_db(transaction=True, databases=["default", METABASE_DATABASE_NAME])
def test_synchronise_une_entreprise_qualifiee_appartenant_a_un_groupe(
    entreprise_factory,
):
    entreprise_factory(
        appartient_groupe=True,
        societe_mere_en_france=True,
        comptes_consolides=True,
        effectif_groupe=CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249,
        effectif_permanent=CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_50,
        tranche_chiffre_affaires_consolide=CaracteristiquesAnnuelles.CA_MOINS_DE_700K,
        tranche_bilan_consolide=CaracteristiquesAnnuelles.BILAN_MOINS_DE_350K,
    )

    Command().handle()

    assert MetabaseEntreprise.objects.count() == 1
    metabase_entreprise = MetabaseEntreprise.objects.first()
    assert metabase_entreprise.appartient_groupe
    assert metabase_entreprise.societe_mere_en_france
    assert metabase_entreprise.comptes_consolides
    assert (
        metabase_entreprise.effectif_groupe
        == CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249
    )
    assert (
        metabase_entreprise.effectif_groupe_permanent
        == CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_50
    )
    assert (
        metabase_entreprise.tranche_chiffre_affaires_consolide
        == CaracteristiquesAnnuelles.CA_MOINS_DE_700K
    )
    assert (
        metabase_entreprise.tranche_bilan_consolide
        == CaracteristiquesAnnuelles.BILAN_MOINS_DE_350K
    )


@pytest.mark.django_db(transaction=True, databases=["default", METABASE_DATABASE_NAME])
def test_synchronise_une_entreprise_plusieurs_fois(entreprise_factory):
    entreprise = entreprise_factory(
        siren="000000001",
        denomination="Entreprise A",
    )

    Command().handle()
    Command().handle()

    assert MetabaseEntreprise.objects.count() == 1
    metabase_entreprise = MetabaseEntreprise.objects.first()
    assert metabase_entreprise.impact_id == entreprise.pk
    assert metabase_entreprise.siren == "000000001"
    assert metabase_entreprise.denomination == "Entreprise A"


@pytest.mark.django_db(transaction=True, databases=["default", METABASE_DATABASE_NAME])
def test_synchronise_une_entreprise_sans_caracteristiques_annuelles():
    entreprise = Entreprise.objects.create(
        siren="000000001", denomination="Entreprise SAS"
    )

    Command().handle()

    metabase_entreprise = MetabaseEntreprise.objects.first()
    assert metabase_entreprise.denomination == "Entreprise SAS"
    assert metabase_entreprise.siren == "000000001"
    assert metabase_entreprise.date_cloture_exercice is None
    assert metabase_entreprise.effectif is None
    assert metabase_entreprise.effectif_permanent is None
    assert metabase_entreprise.effectif_groupe is None
    assert metabase_entreprise.effectif_groupe_permanent is None
    assert metabase_entreprise.tranche_chiffre_affaires is None
    assert metabase_entreprise.tranche_bilan is None
    assert metabase_entreprise.bdese_accord is None
    assert metabase_entreprise.systeme_management_energie is None


@pytest.mark.django_db(transaction=True, databases=["default", METABASE_DATABASE_NAME])
def test_synchronise_une_entreprise_sans_caracteristiques_qualifiantes(
    entreprise_factory,
):
    # Ce cas arrive lorsqu'on ajoute une nouvelle caracteristique qualifiante dans les caracteristiques annuelles
    # Les anciennes caracteristiques ne sont plus qualifiantes mais on veut quand même les avoir dans metabase
    entreprise = entreprise_factory()
    caracteristiques = entreprise.dernieres_caracteristiques_qualifiantes
    tranche_bilan = caracteristiques.tranche_bilan
    caracteristiques.tranche_chiffre_affaires = None
    caracteristiques.save()

    Command().handle()

    metabase_entreprise = MetabaseEntreprise.objects.first()
    assert metabase_entreprise.tranche_bilan == tranche_bilan
    assert metabase_entreprise.tranche_chiffre_affaires is None


@pytest.mark.django_db(transaction=True, databases=["default", METABASE_DATABASE_NAME])
def test_synchronise_une_entreprise_avec_un_utilisateur(
    entreprise_factory, django_user_model
):
    entreprise = entreprise_factory()
    utilisateur = django_user_model.objects.create(
        prenom="Alice",
        nom="Cooper",
        email="alice@impact.test",
        reception_actualites=False,
        is_email_confirmed=True,
    )
    habilitation = attach_user_to_entreprise(utilisateur, entreprise, "Présidente")

    Command().handle()

    metabase_entreprise = MetabaseEntreprise.objects.first()
    assert metabase_entreprise.nombre_utilisateurs == 1

    assert MetabaseUtilisateur.objects.count() == 1
    metabase_utilisateur = MetabaseUtilisateur.objects.first()
    assert metabase_utilisateur.pk == metabase_utilisateur.impact_id == utilisateur.pk
    assert metabase_utilisateur.ajoute_le == utilisateur.created_at
    assert metabase_utilisateur.modifie_le == utilisateur.updated_at
    assert metabase_utilisateur.connecte_le == utilisateur.last_login
    assert metabase_utilisateur.reception_actualites is False
    assert metabase_utilisateur.email_confirme is True
    assert metabase_utilisateur.nombre_entreprises == 1

    assert MetabaseHabilitation.objects.count() == 1
    metabase_habilitation = MetabaseHabilitation.objects.first()
    assert (
        metabase_habilitation.pk == metabase_habilitation.impact_id == habilitation.pk
    )
    assert metabase_habilitation.ajoutee_le == habilitation.created_at
    assert metabase_habilitation.modifiee_le == habilitation.updated_at
    assert metabase_habilitation.utilisateur == metabase_utilisateur
    assert metabase_habilitation.entreprise == metabase_entreprise
    assert metabase_habilitation.fonctions == "Présidente"
    assert not metabase_habilitation.confirmee_le


@pytest.mark.django_db(transaction=True, databases=["default", METABASE_DATABASE_NAME])
def test_synchronise_les_reglementations_BDESE(
    alice, bob, entreprise_factory, bdese_factory
):
    entreprise_non_soumise = entreprise_factory(
        siren="000000001", effectif=CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_50
    )
    entreprise_soumise_a_actualiser = entreprise_factory(
        siren="000000002", effectif=CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249
    )
    entreprise_soumise_en_cours = entreprise_factory(
        siren="000000003", effectif=CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249
    )
    entreprise_soumise_2_utilisateurs = entreprise_factory(
        siren="000000004", effectif=CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249
    )
    for entreprise in (
        entreprise_non_soumise,
        entreprise_soumise_a_actualiser,
        entreprise_soumise_en_cours,
        entreprise_soumise_2_utilisateurs,
    ):
        attach_user_to_entreprise(alice, entreprise, "Présidente")
    bdese_a_actualiser = bdese_factory(
        bdese_class=BDESE_50_300,
        entreprise=entreprise_soumise_a_actualiser,
        annee=derniere_annee_a_remplir_bdese(),
    )
    bdese_en_cours = bdese_factory(
        bdese_class=BDESE_50_300,
        entreprise=entreprise_soumise_en_cours,
        user=alice,
        annee=derniere_annee_a_remplir_bdese(),
    )
    bdese_a_jour_alice = bdese_factory(
        bdese_class=BDESE_50_300,
        entreprise=entreprise_soumise_2_utilisateurs,
        user=alice,
        annee=derniere_annee_a_remplir_bdese(),
    )
    bdese_en_cours_bob = bdese_factory(
        bdese_class=BDESE_50_300,
        entreprise=entreprise_soumise_2_utilisateurs,
        user=bob,
        annee=derniere_annee_a_remplir_bdese(),
    )
    for step in bdese_a_jour_alice.STEPS:
        bdese_a_jour_alice.mark_step_as_complete(step)
    bdese_a_jour_alice.save()

    Command().handle()

    assert MetabaseBDESE.objects.count() == 5

    metabase_bdese_entreprise_non_soumise = MetabaseBDESE.objects.get(
        entreprise__siren=entreprise_non_soumise.siren
    )
    assert not metabase_bdese_entreprise_non_soumise.est_soumise
    assert metabase_bdese_entreprise_non_soumise.statut is None

    metabase_bdese_entreprise_soumise_a_actualiser = MetabaseBDESE.objects.get(
        entreprise__siren=entreprise_soumise_a_actualiser.siren
    )
    assert metabase_bdese_entreprise_soumise_a_actualiser.est_soumise
    assert (
        metabase_bdese_entreprise_soumise_a_actualiser.statut
        == MetabaseBDESE.STATUT_A_ACTUALISER
    )

    metabase_bdese_entreprise_soumise_en_cours = MetabaseBDESE.objects.get(
        entreprise__siren=entreprise_soumise_en_cours.siren
    )
    assert metabase_bdese_entreprise_soumise_en_cours.est_soumise
    assert (
        metabase_bdese_entreprise_soumise_en_cours.statut
        == MetabaseBDESE.STATUT_EN_COURS
    )

    metabase_bdese_entreprise_soumise_2_utilisateurs = MetabaseBDESE.objects.filter(
        entreprise__siren=entreprise_soumise_2_utilisateurs.siren
    )
    assert metabase_bdese_entreprise_soumise_2_utilisateurs.count() == 2
    assert metabase_bdese_entreprise_soumise_2_utilisateurs[
        0
    ].utilisateur == MetabaseUtilisateur.objects.get(pk=alice.pk)
    assert metabase_bdese_entreprise_soumise_2_utilisateurs[0].est_soumise
    assert (
        metabase_bdese_entreprise_soumise_2_utilisateurs[0].statut
        == MetabaseBDESE.STATUT_A_JOUR
    )
    assert metabase_bdese_entreprise_soumise_2_utilisateurs[
        1
    ].utilisateur == MetabaseUtilisateur.objects.get(pk=bob.pk)
    assert metabase_bdese_entreprise_soumise_2_utilisateurs[1].est_soumise
    assert (
        metabase_bdese_entreprise_soumise_2_utilisateurs[1].statut
        == MetabaseBDESE.STATUT_EN_COURS
    )
