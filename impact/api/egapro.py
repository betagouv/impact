import requests
import sentry_sdk

from api.exceptions import APIError

EGAPRO_TIMEOUT = 10


def indicateurs_bdese(siren, annee):
    EGAPRO_INDICATEURS = {
        "promotions": "Écart taux promotion",
        "augmentations_et_promotions": "Écart taux d'augmentation",
        "rémunérations": "Écart rémunérations",
        "congés_maternité": "Retour congé maternité",
        "hautes_rémunérations": "Hautes rémunérations",
    }
    bdese_data_from_egapro = {
        "nombre_femmes_plus_hautes_remunerations": None,
        "objectifs_progression": None,
    }
    try:
        url = f"https://egapro.travail.gouv.fr/api/public/declaration/{siren}/{annee}"
        response = requests.get(url, timeout=EGAPRO_TIMEOUT)
    except Exception as e:
        with sentry_sdk.push_scope() as scope:
            scope.set_level("info")
            sentry_sdk.capture_exception(e)
        raise APIError()

    match response.status_code:
        case 200:
            egapro_data_indicateurs = response.json().get("indicateurs", {})
            if indicateur_hautes_remunerations := egapro_data_indicateurs.get(
                "hautes_rémunérations"
            ):
                bdese_data_from_egapro["nombre_femmes_plus_hautes_remunerations"] = (
                    int(indicateur_hautes_remunerations["résultat"])
                    if indicateur_hautes_remunerations["population_favorable"]
                    == "hommes"
                    else 10 - int(indicateur_hautes_remunerations["résultat"])
                )

            objectifs_progression = {}
            for egapro_indicateur, data in egapro_data_indicateurs.items():
                if objectif := data["objectif_de_progression"]:
                    objectifs_progression[
                        EGAPRO_INDICATEURS[egapro_indicateur]
                    ] = objectif
            if objectifs_progression:
                bdese_data_from_egapro["objectifs_progression"] = "\n".join(
                    f"{egapro_indicateur} : {objectif}"
                    for egapro_indicateur, objectif in objectifs_progression.items()
                )
        case 404:
            pass
        case 400:
            sentry_sdk.capture_message(
                "Requête invalide sur l'API index EgaPro (indicateurs)"
            )
            raise APIError()
        case _:
            sentry_sdk.capture_message("Erreur API index EgaPro (indicateurs)")
            raise APIError()
    return bdese_data_from_egapro


def is_index_egapro_published(siren, annee):
    try:
        url = f"https://egapro.travail.gouv.fr/api/public/declaration/{siren}/{annee}"
        response = requests.get(url, timeout=EGAPRO_TIMEOUT)
    except Exception as e:
        with sentry_sdk.push_scope() as scope:
            scope.set_level("info")
            sentry_sdk.capture_exception(e)
        raise APIError()
    match response.status_code:
        case 200:
            return "déclaration" in response.json()
        case 404:
            pass
        case 400:
            sentry_sdk.capture_message(
                "Requête invalide sur l'API index EgaPro (is_index_egapro_published)"
            )
            raise APIError()
        case _:
            sentry_sdk.capture_message(
                "Erreur API index EgaPro (is_index_egapro_published)"
            )
            raise APIError()
    return False
