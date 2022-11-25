from django import forms
from django.core.exceptions import ValidationError
import json

from public.forms import DsfrForm
from .models import BDESE_50_300, BDESE_300


class ListJSONWidget(forms.widgets.MultiWidget):
    def decompress(self, value):
        if isinstance(value, list):
            return value
        elif isinstance(value, str) and value != "null":
            values = json.loads(value)
            value = [value for value in values if value is not None]
            return value
        return []

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        not_empty_values = [value for value in values if value]
        # JSONField expects a single string that it can parse into json.
        return json.dumps(not_empty_values)


class CategoriesProfessionnellesForm(forms.ModelForm, DsfrForm):
    class Meta:
        fields = ["categories_professionnelles"]

    def clean_categories_professionnelles(self):
        data = self.cleaned_data["categories_professionnelles"]
        if len(data) < 3:
            raise ValidationError("Au moins 3 catégories sont requises")
        return data


def categories_professionnelles_form_factory(
    bdese, *args, number_categories=3, **kwargs
):
    widgets = [
        forms.widgets.TextInput(attrs={"class": "fr-input"})
        for i in range(number_categories)
    ]

    Form = forms.modelform_factory(
        bdese.__class__,
        form=CategoriesProfessionnellesForm,
        widgets={"categories_professionnelles": ListJSONWidget(widgets)},
    )
    return Form(*args, instance=bdese, **kwargs)


class CategoryJSONWidget(forms.MultiWidget):
    template_name = "snippets/category_json_widget.html"

    def __init__(self, categories, widgets=None, attrs=None):
        self.categories = categories
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if type(value) != dict:
            return []
        return [value.get(category) for category in self.categories]


def bdese_form_factory(
    step, categories_professionnelles, instance, fetched_data=None, *args, **kwargs
):
    class CategoryMultiValueField(forms.MultiValueField):
        widget = CategoryJSONWidget

        def __init__(
            self,
            base_field=forms.IntegerField,
            categories=None,
            encoder=None,
            decoder=None,
            *args,
            **kwargs
        ):
            """https://docs.djangoproject.com/en/4.1/ref/forms/fields/#django.forms.MultiValueField.require_all_fields"""
            self.categories = categories or categories_professionnelles
            fields = [base_field() for category in self.categories]
            widgets = [
                base_field.widget({"label": category})
                for category in self.categories
                if hasattr(base_field, "widget")
            ]
            super().__init__(
                fields=fields,
                widget=CategoryJSONWidget(
                    self.categories, widgets, attrs={"class": "fr-input"}
                ),
                require_all_fields=False,
                *args,
                **kwargs
            )

        def compress(self, data_list):
            if data_list:
                return dict(zip(self.categories, data_list))
            return None

    class BDESEForm(forms.ModelForm, DsfrForm):
        class Meta:
            model = instance.__class__
            fields = []
            field_classes = {
                category_field: CategoryMultiValueField
                for category_field in instance.__class__.category_fields()
            }

        def __init__(self, instance, fetched_data=None, *args, **kwargs):
            if fetched_data:
                if "initial" not in kwargs:
                    kwargs["initial"] = {}
                kwargs["initial"].update(fetched_data)
            super().__init__(instance=instance, *args, **kwargs)
            if step == "all" or instance.step_is_complete(step):
                for field in self.fields:
                    self.fields[field].disabled = True
            elif fetched_data:
                for field in fetched_data:
                    if field in self.fields:
                        self.fields[
                            field
                        ].help_text += " (valeur extraite de Index EgaPro)"
                        self.fields[field].disabled = True

    fields = {
        1: [
            "effectif_total",
            "effectif_permanent",
            "effectif_cdd",
            "effectif_mensuel_moyen",
            "effectif_homme",
            "effectif_femme",
            "effectif_age",
            "effectif_anciennete",
            "effectif_nationalite_francaise",
            "effectif_nationalite_etrangere",
            "nombre_travailleurs_exterieurs",
            "nombre_stagiaires",
            "nombre_moyen_mensuel_salaries_temporaires",
            "duree_moyenne_contrat_de_travail_temporaire",
            "nombre_salaries_de_l_entreprise_detaches",
            "nombre_salaries_detaches_accueillis",
            "nombre_embauches_cdi",
            "nombre_embauches_cdd",
            "nombre_embauches_jeunes",
            "total_departs",
            "nombre_demissions",
            "nombre_licenciements_economiques",
            "nombre_licenciements_autres",
            "nombre_fin_cdd",
            "nombre_fin_periode_essai",
            "nombre_mutations",
            "nombre_departs_volontaires_retraite_preretraite",
            "nombre_deces",
            "nombre_promotions",
            "nombre_salaries_chomage_partiel",
            "nombre_heures_chomage_partiel_indemnisees",
            "nombre_heures_chomage_partiel_non_indemnisees",
            "nombre_salaries_chomage_intemperies",
            "nombre_heures_chomage_intemperies_indemnisees",
            "nombre_heures_chomage_intemperies_non_indemnisees",
            "nombre_travailleurs_handicapés",
            "nombre_travailleurs_handicapes_accidents_du_travail",
            "pourcentage_masse_salariale_formation_continue",
            "montant_formation_continue",
            "nombre_heures_stage_remunerees",
            "nombre_heures_stage_non_remunerees",
            "type_stages",
            "nombre_salaries_conge_formation_remunere",
            "nombre_salaries_conge_formation_non_remunere",
            "nombre_salaries_conge_formation_refuse",
            "nombre_contrats_apprentissage",
            "nombre_incapacites_permanentes_partielles",
            "nombre_incapacites_permanentes_totales",
            "nombre_accidents_travail_mortels",
            "nombre_accidents_trajet_mortels",
            "nombre_accidents_trajet_avec_arret_travail",
            "nombre_accidents_salaries_temporaires_ou_prestataires",
            "taux_cotisation_securite_sociale_accidents_travail",
            "montant_cotisation_securite_sociale_accidents_travail",
            "nombre_accidents_existence_risques_graves",
            "nombre_accidents_chutes_dénivellation",
            "nombre_accidents_machines",
            "nombre_accidents_circulation_manutention_stockage",
            "nombre_accidents_objets_en_mouvement",
            "nombre_accidents_autres",
            "nombre_maladies_professionnelles",
            "denomination_maladies_professionnelles",
            "nombre_salaries_affections_pathologiques",
            "caracterisation_affections_pathologiques",
            "nombre_declaration_procedes_travail_dangereux",
            "effectif_forme_securite",
            "montant_depenses_formation_securite",
            "taux_realisation_programme_securite",
            "nombre_plans_specifiques_securite",
            "horaire_hebdomadaire_moyen",
            "nombre_salaries_repos_compensateur_code_travail",
            "nombre_salaries_repos_compensateur_regime_conventionne",
            "nombre_salaries_horaires_individualises",
            "nombre_salaries_temps_partiel_20_30_heures",
            "nombre_salaries_temps_partiel_autres",
            "nombre_salaries_2_jours_repos_hebdomadaire_consecutifs",
            "nombre_moyen_jours_conges_annuels",
            "nombre_jours_feries_payes",
            "unite_absenteisme",
            "nombre_unites_absence",
            "nombre_unites_theoriques_travaillees",
            "nombre_unites_absence_maladie",
            "nombre_unites_absence_accidents",
            "nombre_unites_absence_maternite",
            "nombre_unites_absence_conges_autorises",
            "nombre_unites_absence_autres",
            "nombre_personnes_horaires_alternant_ou_nuit",
            "nombre_personnes_horaires_alternant_ou_nuit_50_ans",
            "nombre_taches_repetitives",
            "nombre_personnes_exposees_bruit",
            "nombre_salaries_exposes_temperatures",
            "nombre_salaries_exposes_temperatures_extremes",
            "nombre_salaries_exposes_intemperies",
            "nombre_analyses_produits_toxiques",
            "experiences_transformation_organisation_travail",
            "montant_depenses_amelioration_conditions_travail",
            "taux_realisation_programme_amelioration_conditions_travail",
            "nombre_visites_medicales",
            "nombre_examens_medicaux",
            "pourcentage_temps_medecin_du_travail",
            "nombre_salaries_inaptes",
            "nombre_salaries_reclasses",
        ],
        2: [
            "evolution_amortissement",
            "montant_depenses_recherche_developpement",
            "evolution_productivite",
        ],
        3: [
            "nombre_CDI_homme",
            "nombre_CDI_femme",
            "nombre_CDD_homme",
            "nombre_CDD_femme",
            "effectif_par_duree_homme",
            "effectif_par_duree_femme",
            "effectif_par_organisation_du_travail_homme",
            "effectif_par_organisation_du_travail_femme",
            "conges_homme",
            "conges_femme",
            "conges_par_type_homme",
            "conges_par_type_femme",
            "embauches_CDI_homme",
            "embauches_CDI_femme",
            "embauches_CDD_homme",
            "embauches_CDD_femme",
            "departs_retraite_homme",
            "departs_demission_homme",
            "departs_fin_CDD_homme",
            "departs_licenciement_homme",
            "departs_retraite_femme",
            "departs_demission_femme",
            "departs_fin_CDD_femme",
            "departs_licenciement_femme",
            "nombre_promotions_homme",
            "nombre_promotions_femme",
            "duree_moyenne_entre_deux_promotions_homme",
            "duree_moyenne_entre_deux_promotions_femme",
            "anciennete_moyenne_homme",
            "anciennete_moyenne_femme",
            "anciennete_moyenne_dans_categorie_profesionnelle_homme",
            "anciennete_moyenne_dans_categorie_profesionnelle_femme",
            "age_moyen_homme",
            "age_moyen_femme",
            "remuneration_moyenne_homme",
            "remuneration_moyenne_femme",
            "remuneration_moyenne_par_age_homme",
            "remuneration_moyenne_par_age_femme",
            "nombre_femmes_plus_hautes_remunerations",
            "nombre_moyen_heures_formation_homme",
            "nombre_moyen_heures_formation_femme",
            "action_adaptation_au_poste_homme",
            "action_adaptation_au_poste_femme",
            "action_maintien_emploi_homme",
            "action_maintien_emploi_femme",
            "action_developpement_competences_homme",
            "action_developpement_competences_femme",
            "exposition_risques_pro_homme",
            "exposition_risques_pro_femme",
            "accidents_homme",
            "accidents_femme",
            "nombre_accidents_travail_avec_arret_homme",
            "nombre_accidents_travail_avec_arret_femme",
            "nombre_accidents_trajet_avec_arret_homme",
            "nombre_accidents_trajet_avec_arret_femme",
            "nombre_accidents_par_elements_materiels_homme",
            "nombre_accidents_par_elements_materiels_femme",
            "nombre_et_denominations_maladies_pro_homme",
            "nombre_et_denominations_maladies_pro_femme",
            "nombre_journees_absence_accident_homme",
            "nombre_journees_absence_accident_femme",
            "maladies_homme",
            "maladies_femme",
            "maladies_avec_examen_de_reprise_homme",
            "maladies_avec_examen_de_reprise_femme",
            "complement_salaire_conge",
            "nombre_jours_conges_paternite_pris",
            "existence_orga_facilitant_vie_familiale_et_professionnelle",
            "nombre_salaries_temps_partiel_choisi_homme",
            "nombre_salaries_temps_partiel_choisi_femme",
            "nombre_salaries_temps_partiel_choisi_vers_temps_plein_homme",
            "nombre_salaries_temps_partiel_choisi_vers_temps_plein_femme",
            "participation_accueil_petite_enfance",
            "evolution_depenses_credit_impot_famille",
            "mesures_prises_egalite",
            "objectifs_progression",
        ],
        4: [
            "capitaux_propres",
            "emprunts_et_dettes_financieres",
            "impots_et_taxes",
        ],
        5: [
            "frais_personnel",
            "evolution_salariale_par_categorie",
            "evolution_salariale_par_sexe",
            "salaire_base_minimum_par_categorie",
            "salaire_base_minimum_par_sexe",
            "salaire_moyen_par_categorie",
            "salaire_moyen_par_sexe",
            "salaire_median_par_categorie",
            "salaire_median_par_sexe",
            "rapport_masse_salariale_effectif_mensuel",
            "remuneration_moyenne_decembre",
            "remuneration_mensuelle_moyenne",
            "part_primes_non_mensuelle",
            "remunerations",
            "rapport_moyenne_deciles",
            "rapport_moyenne_cadres_ouvriers",
            "montant_10_remunerations_les_plus_eleves",
            "pourcentage_salaries_primes_de_rendement",
            "pourcentage_ouvriers_employes_payes_au_mois",
            "charge_salariale_globale",
            "montant_global_hautes_remunerations",
            "montant_global_reserve_de_participation",
            "montant_moyen_participation",
            "part_capital_detenu_par_salaries",
            "avantages_sociaux",
            "remuneration_dirigeants_mandataires_sociaux",
        ],
        6: [
            "composition_CSE_etablissement",
            "participation_elections",
            "volume_credit_heures",
            "nombre_reunion_representants_personnel",
            "accords_conclus",
            "nombre_personnes_conge_education_ouvriere",
            "nombre_heures_reunion_personnel",
            "elements_systeme_accueil",
            "elements_systeme_information",
            "elements_systeme_entretiens_individuels",
            "differends_application_droit_du_travail",
            "contributions_financement_CSE_CSEE",
            "contributions_autres_depenses",
            "cout_prestations_maladie_deces",
            "cout_prestations_vieillesse",
            "equipements_pour_conditions_de_vie",
        ],
        7: ["remuneration_actionnaires", "remuneration_actionnariat_salarie"],
        8: [
            "aides_financieres",
            "reductions_impots",
            "exonerations_cotisations_sociales",
            "credits_impots",
            "mecenat",
            "chiffre_affaires",
            "benefices_ou_pertes",
            "resultats_globaux",
            "affectation_benefices",
        ],
        9: ["partenariats_pour_produire", "partenariats_pour_beneficier"],
        10: ["transferts_de_capitaux", "cessions_fusions_acquisitions"],
        11: [
            "informations_environnementales",
            "prevention_et_gestion_dechets",
            "bilan_gaz_effet_de_serre",
            "prise_en_compte_questions_environnementales",
            "quantite_de_dechets_dangereux",
            "consommation_eau",
            "consommation_energie",
            "postes_emissions_directes_gaz_effet_de_serre",
            "bilan_gaz_effet_de_serre",
        ],
    }

    bdese_model_class = instance.__class__
    Form = forms.modelform_factory(
        bdese_model_class,
        form=BDESEForm,
        fields=fields[step]
        if bdese_model_class == BDESE_300 and step != "all"
        else "__all__",
        exclude=None
        if bdese_model_class == BDESE_300
        else ["annee", "entreprise", "categories_professionnelles"],
    )
    return Form(instance, fetched_data=fetched_data, *args, **kwargs)
