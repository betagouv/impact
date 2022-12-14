from django.urls import path

from . import views

urlpatterns = [
    path("reglementations", views.reglementations, name="reglementations"),
    path(
        "bdese/<str:siren>/<int:annee>/0",
        views.categories_professionnelles,
        name="categories_professionnelles",
    ),
    path("bdese/<str:siren>/<int:annee>/<int:step>", views.bdese, name="bdese"),
    path("bdese/<str:siren>/<int:annee>/pdf", views.bdese_pdf, name="bdese_pdf"),
]
