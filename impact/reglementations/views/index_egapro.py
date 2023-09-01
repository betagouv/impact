from django.conf import settings

from api import egapro
from entreprises.models import CaracteristiquesAnnuelles
from habilitations.models import is_user_attached_to_entreprise
from reglementations.models import derniere_annee_a_remplir_index_egapro
from reglementations.views.base import Reglementation
from reglementations.views.base import ReglementationAction
from reglementations.views.base import ReglementationStatus


class IndexEgaproReglementation(Reglementation):
    title = "Index de l’égalité professionnelle"
    description = "Afin de lutter contre les inégalités salariales entre les femmes et les hommes, certaines entreprises doivent calculer et transmettre un index mesurant l’égalité salariale au sein de leur structure."
    more_info_url = "https://www.economie.gouv.fr/entreprises/index-egalite-professionnelle-obligatoire"

    @classmethod
    def est_soumis(cls, caracteristiques):
        return (
            caracteristiques.effectif != CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_50
        )

    @classmethod
    def calculate_status(
        cls,
        caracteristiques: CaracteristiquesAnnuelles,
        user: settings.AUTH_USER_MODEL,
    ) -> ReglementationStatus:

        NON_SOUMIS_PRIMARY_ACTION = ReglementationAction(
            "https://egapro.travail.gouv.fr/index-egapro/recherche",
            "Consulter les index sur la plateforme Egapro",
            external=True,
        )

        if not user.is_authenticated:
            return cls.calculate_status_for_anonymous_user(
                caracteristiques, primary_action=NON_SOUMIS_PRIMARY_ACTION
            )
        elif not is_user_attached_to_entreprise(user, caracteristiques.entreprise):
            return cls.calculate_status_for_unauthorized_user(caracteristiques)

        if not cls.est_soumis(caracteristiques):
            status = ReglementationStatus.STATUS_NON_SOUMIS
            status_detail = "Vous n'êtes pas soumis à cette réglementation."
            primary_action = NON_SOUMIS_PRIMARY_ACTION
        else:
            primary_action = ReglementationAction(
                "https://egapro.travail.gouv.fr/",
                "Calculer et déclarer mon index sur la plateforme Egapro",
                external=True,
            )
            if egapro.is_index_egapro_published(
                caracteristiques.entreprise.siren,
                derniere_annee_a_remplir_index_egapro(),
            ):
                status = ReglementationStatus.STATUS_A_JOUR
                status_detail = "Vous êtes soumis à cette réglementation car votre effectif est supérieur à 50 salariés. Vous avez rempli vos obligations d'après les données disponibles sur la plateforme Egapro."
            else:
                status = ReglementationStatus.STATUS_A_ACTUALISER
                status_detail = "Vous êtes soumis à cette réglementation car votre effectif est supérieur à 50 salariés. Vous n'avez pas encore déclaré votre index sur la plateforme Egapro."
        return ReglementationStatus(
            status, status_detail, primary_action=primary_action
        )
