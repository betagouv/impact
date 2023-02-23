from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EntrepriseCreationForm
from .models import Entreprise, Habilitation
from api.exceptions import APIError

import api.recherche_entreprises


@login_required()
def index(request):
    form = EntrepriseCreationForm()
    return render(request, "entreprises/index.html", {"form": form})


class _InvalidRequest(Exception):
    pass


@login_required()
def add(request):
    form = EntrepriseCreationForm(request.POST)
    try:
        if form.is_valid():
            siren = form.cleaned_data["siren"]
            if entreprises := Entreprise.objects.filter(siren=siren):
                entreprise = entreprises[0]
            else:
                try:
                    infos_entreprise = api.recherche_entreprises.recherche(siren)
                except APIError:
                    raise _InvalidRequest(
                        "Impossible de créer l'entreprise car le SIREN n'est pas trouvé."
                    )
                entreprise = Entreprise.objects.create(**infos_entreprise)
            Habilitation.objects.create(
                user=request.user,
                entreprise=entreprise,
            )
        else:
            raise _InvalidRequest(
                "Impossible de créer l'entreprise car les données sont incorrectes."
            )
    except _InvalidRequest as exception:
        messages.error(
            request,
            exception,
        )
        return render(request, "entreprises/index.html", {"form": form})

    messages.success(request, "L'entreprise a été ajoutée.")
    return redirect("entreprises")
