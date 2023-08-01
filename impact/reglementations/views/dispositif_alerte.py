from django.conf import settings

from entreprises.models import CaracteristiquesAnnuelles
from reglementations.views.base import Reglementation
from reglementations.views.base import ReglementationStatus


class DispositifAlerteReglementation(Reglementation):
    title = "Dispositif d'alerte"
    description = "Un dispositif d’alertes professionnelles (ou DAP) est un outil permettant à une personne (salarié, cocontractant, tiers…) de porter à la connaissance d’un organisme une situation, un comportement ou un risque susceptible de caractériser une infraction ou une violation de règles éthiques adoptées par l’organisme en question, tel qu’un manquement à une charte ou à un code de conduite. Les entreprises de plus de 50 salariés doivent mettre en place depuis le 1er septembre 2022 des dispositifs d’alerte sécurisés qui garantissent la confidentialité de l’identité de l’auteur du signalement."
    more_info_url = "https://www.service-public.fr/particuliers/vosdroits/F32031"

    def est_soumis(self, caracteristiques):
        return (
            caracteristiques.effectif != CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_50
        )

    def calculate_status(
        self,
        caracteristiques: CaracteristiquesAnnuelles,
        user: settings.AUTH_USER_MODEL,
    ) -> ReglementationStatus:
        if reglementation_status := super().calculate_status(caracteristiques, user):
            return reglementation_status

        if self.est_soumis(caracteristiques):
            status = ReglementationStatus.STATUS_SOUMIS
            status_detail = "Vous êtes soumis à cette réglementation"
        else:
            status = ReglementationStatus.STATUS_NON_SOUMIS
            status_detail = "Vous n'êtes pas soumis à cette réglementation"
        return ReglementationStatus(status, status_detail)