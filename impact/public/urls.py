from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("entreprise", views.entreprise, name="entreprise"),
    path("siren", views.siren, name="siren"),
    path("mentions-legales", views.mentions_legales, name="mentions_legales"),
    path(
        "politique-confidentialite",
        views.politique_confidentialite,
        name="politique_confidentialite",
    ),
    path("cgu", views.cgu, name="cgu"),
    path("contact", views.contact, name="contact"),
]
