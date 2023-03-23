from datetime import datetime
from datetime import timezone

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from entreprises.models import Entreprise
from reglementations.models import get_all_personal_bdese
from reglementations.models import has_official_bdese


FONCTIONS_MAX_LENGTH = 250


class Habilitation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    fonctions = models.CharField(
        verbose_name="Fonction(s) dans la société",
        max_length=FONCTIONS_MAX_LENGTH,
        null=True,
        blank=True,
    )
    confirmed_at = models.DateTimeField(null=True)

    def confirm(self):
        self.confirmed_at = datetime.now(timezone.utc)
        if not has_official_bdese(self.entreprise):
            for bdese in get_all_personal_bdese(self.entreprise, self.user):
                bdese.officialize()

    def unconfirm(self):
        self.confirmed_at = None

    @property
    def is_confirmed(self):
        return bool(self.confirmed_at)


def attach_entreprise_to_user(entreprise, user, fonctions):
    Habilitation.objects.create(
        user=user,
        entreprise=entreprise,
        fonctions=fonctions,
    )


def detach_entreprise_from_user(entreprise, user):
    get_habilitation(entreprise, user).delete()


def get_habilitation(entreprise, user):
    return Habilitation.objects.get(
        user=user,
        entreprise=entreprise,
    )


def is_user_attached_to_entreprise(user, entreprise):
    try:
        get_habilitation(entreprise, user)
        return True
    except ObjectDoesNotExist:
        return False


def is_user_habilited_on_entreprise(user, entreprise):
    return (
        is_user_attached_to_entreprise(user, entreprise)
        and get_habilitation(entreprise, user).is_confirmed
    )
