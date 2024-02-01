from datetime import datetime

import requests
import sentry_sdk


def last_reporting(siren):
    response = requests.get(
        "https://bilans-ges.ademe.fr/api/inventories",
        params={"page": "1", "itemsPerPage": "11", "entity.siren": siren},
    )
    if response.status_code != 200:
        sentry_sdk.capture_message(f"Erreur API bilans-ges ({siren})")
        return

    try:
        data = response.json()
        if members := data["hydra:member"]:
            first_member = members[0]
            last_reporting_year = first_member["identitySheet"]["reportingYear"]
            publicated_at = first_member["publication"]["publicatedAt"]
            for member in members[1:]:
                year = member["identitySheet"]["reportingYear"]
                if year > last_reporting_year:
                    last_reporting_year = year
                    publicated_at = member["publication"]["publicatedAt"]
            return {
                "year": last_reporting_year,
                "publication_date": datetime.fromisoformat(publicated_at).date(),
            }
    except Exception as e:
        sentry_sdk.capture_exception(e)
