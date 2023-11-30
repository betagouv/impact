from django.conf import settings
from django.urls import reverse_lazy

from entreprises.models import CaracteristiquesAnnuelles
from entreprises.models import CategorieJuridique
from entreprises.models import convertit_categorie_juridique
from reglementations.views.base import Reglementation
from reglementations.views.base import ReglementationStatus


class DPEFReglementation(Reglementation):
    title = "Déclaration de Performance Extra-Financière"
    description = """La Déclaration de Performance Extra-Financière (dite "DPEF") est un document par l'intermédiaire duquel une entreprise détaille les implications sociales, environnementales et sociétales de sa performance et de ses activités, ainsi que son mode de gouvernance."""
    more_info_url = reverse_lazy("reglementations:fiche_dpef")
    tag = "tag-durabilite"
    summary = "Établir une déclaration de performance extra-financière contenant des informations sociales, environnementales et sociétales."

    CRITERE_EFFECTIF_PERMANENT = "votre effectif permanent est supérieur à 500 salariés"
    CRITERE_EFFECTIF_GROUPE_PERMANENT = (
        "l'effectif permanent du groupe est supérieur à 500 salariés"
    )

    @classmethod
    def est_suffisamment_qualifiee(cls, caracteristiques):
        return caracteristiques.effectif is not None

    @classmethod
    def calculate_status(
        cls,
        caracteristiques: CaracteristiquesAnnuelles,
        user: settings.AUTH_USER_MODEL,
    ) -> ReglementationStatus:
        if reglementation_status := super().calculate_status(caracteristiques, user):
            return reglementation_status

        if cls.est_soumis(caracteristiques):
            status = ReglementationStatus.STATUS_SOUMIS
            criteres = cls.criteres_remplis(caracteristiques)
            justification = ", ".join(criteres[:-1]) + " et " + criteres[-1]
            status_detail = (
                f"Vous êtes soumis à cette réglementation car {justification}."
            )
        else:
            status = ReglementationStatus.STATUS_NON_SOUMIS
            status_detail = "Vous n'êtes pas soumis à cette réglementation."
        return ReglementationStatus(status, status_detail)

    @classmethod
    def critere_categorie_juridique(cls, caracteristiques):
        categorie_juridique = convertit_categorie_juridique(
            caracteristiques.entreprise.categorie_juridique_sirene
        )
        if categorie_juridique == CategorieJuridique.SOCIETE_ANONYME:
            return "votre entreprise est une Société Anonyme"
        elif categorie_juridique == CategorieJuridique.SOCIETE_COMMANDITE_PAR_ACTIONS:
            return "votre entreprise est une Société en Commandite par Actions"
        elif categorie_juridique == CategorieJuridique.SOCIETE_EUROPEENNE:
            return "votre entreprise est une Société Européenne"

    @classmethod
    def critere_effectif(cls, caracteristiques):
        if caracteristiques.effectif_permanent in (
            CaracteristiquesAnnuelles.EFFECTIF_ENTRE_500_ET_4999,
            CaracteristiquesAnnuelles.EFFECTIF_ENTRE_5000_ET_9999,
            CaracteristiquesAnnuelles.EFFECTIF_10000_ET_PLUS,
        ):
            return cls.CRITERE_EFFECTIF_PERMANENT
        elif (
            caracteristiques.entreprise.comptes_consolides
            and caracteristiques.effectif_groupe_permanent
            in (
                CaracteristiquesAnnuelles.EFFECTIF_ENTRE_500_ET_4999,
                CaracteristiquesAnnuelles.EFFECTIF_ENTRE_5000_ET_9999,
                CaracteristiquesAnnuelles.EFFECTIF_10000_ET_PLUS,
            )
        ):
            return cls.CRITERE_EFFECTIF_GROUPE_PERMANENT

    @classmethod
    def critere_bilan(cls, caracteristiques):
        if caracteristiques.entreprise.est_cotee:
            if caracteristiques.tranche_bilan in (
                CaracteristiquesAnnuelles.BILAN_ENTRE_20M_ET_43M,
                CaracteristiquesAnnuelles.BILAN_ENTRE_43M_ET_100M,
                CaracteristiquesAnnuelles.BILAN_100M_ET_PLUS,
            ):
                return "votre bilan est supérieur à 20M€"
            elif caracteristiques.tranche_bilan_consolide in (
                CaracteristiquesAnnuelles.BILAN_ENTRE_20M_ET_43M,
                CaracteristiquesAnnuelles.BILAN_ENTRE_43M_ET_100M,
                CaracteristiquesAnnuelles.BILAN_100M_ET_PLUS,
            ):
                return "votre bilan consolidé est supérieur à 20M€"
        elif (
            caracteristiques.tranche_bilan
            == CaracteristiquesAnnuelles.BILAN_100M_ET_PLUS
        ):
            return "votre bilan est supérieur à 100M€"
        elif (
            caracteristiques.tranche_bilan_consolide
            == CaracteristiquesAnnuelles.BILAN_100M_ET_PLUS
        ):
            return "votre bilan consolidé est supérieur à 100M€"

    @classmethod
    def critere_chiffre_affaires(cls, caracteristiques):
        if caracteristiques.entreprise.est_cotee:
            if caracteristiques.tranche_chiffre_affaires in (
                CaracteristiquesAnnuelles.CA_ENTRE_40M_ET_50M,
                CaracteristiquesAnnuelles.CA_ENTRE_50M_ET_100M,
                CaracteristiquesAnnuelles.CA_100M_ET_PLUS,
            ):
                return "votre chiffre d'affaires est supérieur à 40M€"
            elif caracteristiques.tranche_chiffre_affaires_consolide in (
                CaracteristiquesAnnuelles.CA_ENTRE_40M_ET_50M,
                CaracteristiquesAnnuelles.CA_ENTRE_50M_ET_100M,
                CaracteristiquesAnnuelles.CA_100M_ET_PLUS,
            ):
                return "votre chiffre d'affaires consolidé est supérieur à 40M€"
        if (
            caracteristiques.tranche_chiffre_affaires
            == CaracteristiquesAnnuelles.CA_100M_ET_PLUS
        ):
            return "votre chiffre d'affaires est supérieur à 100M€"
        elif (
            caracteristiques.tranche_chiffre_affaires_consolide
            == CaracteristiquesAnnuelles.CA_100M_ET_PLUS
        ):
            return "votre chiffre d'affaires consolidé est supérieur à 100M€"

    @classmethod
    def criteres_remplis(cls, caracteristiques):
        criteres = []
        if critere := cls.critere_categorie_juridique(caracteristiques):
            criteres.append(critere)
        if caracteristiques.entreprise.est_cotee:
            criteres.append("votre société est cotée sur un marché réglementé")
        if critere := cls.critere_effectif(caracteristiques):
            criteres.append(critere)
        if critere := cls.critere_bilan(caracteristiques):
            criteres.append(critere)
        if critere := cls.critere_chiffre_affaires(caracteristiques):
            criteres.append(critere)
        return criteres

    @classmethod
    def est_soumis(cls, caracteristiques):
        super().est_soumis(caracteristiques)
        return (
            cls.critere_categorie_juridique(caracteristiques)
            and cls.critere_effectif(caracteristiques)
            and (
                cls.critere_bilan(caracteristiques)
                or cls.critere_chiffre_affaires(caracteristiques)
            )
        )