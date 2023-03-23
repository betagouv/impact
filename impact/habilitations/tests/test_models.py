from datetime import datetime
from datetime import timezone

from freezegun import freeze_time

from habilitations.models import attach_entreprise_to_user
from habilitations.models import get_habilitation
from habilitations.models import is_user_attached_to_entreprise


def test_habilitation(alice, entreprise_factory):
    entreprise = entreprise_factory()
    assert not is_user_attached_to_entreprise(alice, entreprise)

    attach_entreprise_to_user(entreprise, alice, "présidente")

    assert entreprise in alice.entreprises.all()
    habilitation = get_habilitation(entreprise, alice)
    assert habilitation.fonctions == "présidente"

    now = datetime(2023, 1, 27, 16, 1, tzinfo=timezone.utc)
    with freeze_time(now):
        habilitation.confirm()

    assert habilitation.is_confirmed
    assert habilitation.confirmed_at == now
