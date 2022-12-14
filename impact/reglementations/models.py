import datetime
from enum import Enum

from django import forms
from django.db import models

from entreprises.models import Entreprise


def derniere_annee_a_remplir_index_egapro():
    annee = datetime.date.today().year
    return annee - 1


def derniere_annee_a_remplir_bdese():
    annee = datetime.date.today().year
    return annee - 1


def annees_a_remplir_bdese():
    annee = datetime.date.today().year
    return [annee - 3, annee - 2, annee - 1, annee, annee + 1, annee + 2]


class CategoryType(Enum):
    HARD_CODED = 1
    PROFESSIONNELLE = 2
    PROFESSIONNELLE_DETAILLEE = 3


class CategoryField(models.JSONField):
    def __init__(
        self,
        base_field=forms.IntegerField,
        category_type=CategoryType.HARD_CODED,
        categories=None,
        *args,
        **kwargs,
    ):
        self.base_field = base_field
        self.category_type = category_type
        self.categories = categories
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.base_field != forms.IntegerField:
            kwargs["base_field"] = self.base_field
        if self.category_type != CategoryType.HARD_CODED:
            kwargs["category_type"] = self.category_type
        if self.categories:
            kwargs["categories"] = self.categories
        return name, path, args, kwargs

    @property
    def non_db_attrs(self):
        return super().non_db_attrs + (
            "base_field",
            "category_type",
            "categories",
        )

    def formfield(self, **kwargs):
        defaults = {
            "base_field": self.base_field,
            "category_type": self.category_type,
        }
        if self.categories:
            defaults["categories"] = self.categories
        defaults.update(kwargs)
        return super().formfield(**defaults)


class AbstractBDESE(models.Model):
    annee = models.IntegerField()
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    categories_professionnelles = models.JSONField(
        verbose_name="Cat??gories professionnelles",
        help_text="Une structure de qualification d??taill??e en trois postes minimum",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.entreprise} {self.annee}"

    @classmethod
    def category_fields(cls):
        return [
            attribute_name
            for attribute_name in cls.__dict__.keys()
            if hasattr(getattr(cls, attribute_name), "field")
            and type(getattr(cls, attribute_name).field) == CategoryField
        ]

    def mark_step_as_complete(self, step: int):
        pass

    def mark_step_as_incomplete(self, step: int):
        pass

    def step_is_complete(self, step: int):
        return False

    @property
    def is_complete(self):
        return False

    @property
    def is_bdese_300(self):
        return isinstance(self, BDESE_300)


def bdese_300_completion_steps_default():
    return {step_name: False for step_name in BDESE_300.STEPS.values()}


class BDESE_300(AbstractBDESE):
    class Meta:
        verbose_name = "BDESE plus de 300 salari??s"
        verbose_name_plural = "BDESE plus de 300 salari??s"

    STEPS = {
        0: "Cat??gories professionnelles",
        1: "Investissement social",
        2: "Investissement mat??riel et immat??riel",
        3: "Egalit?? professionnelle homme/femme",
        4: "Fonds propres, endettement et imp??ts",
        5: "R??mun??rations",
        6: "Repr??sentation du personnel et Activit??s sociales et culturelles",
        7: "R??mun??ration des financeurs",
        8: "Flux financiers",
        9: "Partenariats",
        10: "Transferts commerciaux et financiers",
        11: "Environnement",
    }

    completion_steps = CategoryField(
        base_field=models.BooleanField,
        categories=list(STEPS.values()),
        default=bdese_300_completion_steps_default,
    )

    categories_professionnelles_detaillees = models.JSONField(
        verbose_name="Cat??gories professionnelles d??taill??es",
        help_text="Une structure de qualification d??taill??e en cinq postes minimum",
        null=True,
        blank=True,
    )

    # D??cret no 2022-678 du 26 avril 2022
    # https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000045680845
    # 1?? Investissements
    # 1?? A - Investissement social
    # 1?? A - a) Evolution des effectifs par type de contrat, par ??ge, par anciennet??
    # 1?? A - a) i - Effectif
    effectif_total = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        help_text="Tout salari?? inscrit ?? l???effectif au 31/12 quelle que soit la nature de son contrat de travail",
        null=True,
        blank=True,
    )
    effectif_permanent = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        help_text="Les salari??s ?? temps plein, inscrits ?? l???effectif pendant toute l???ann??e consid??r??e et titulaires d???un contrat de travail ?? dur??e ind??termin??e.",
        null=True,
        blank=True,
    )
    effectif_cdd = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Effectif CDD",
        help_text="Nombre de salari??s titulaires d???un contrat de travail ?? dur??e d??termin??e au 31/12",
        blank=True,
        null=True,
    )
    effectif_mensuel_moyen = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        help_text="Somme des effectifs totaux mensuels divis??e par 12 (on entend par effectif total tout salari?? inscrit ?? l???effectif au dernier jour du mois consid??r??)",
        null=True,
        blank=True,
    )
    effectif_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        null=True,
        blank=True,
    )
    effectif_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        null=True,
        blank=True,
    )
    effectif_age = CategoryField(
        categories=[
            "moins de 30 ans",
            "30 ?? 39 ans",
            "40 ?? 49 ans",
            "50 ans et plus",
        ],
        verbose_name="Effectif par ??ge",
        null=True,
        blank=True,
    )
    effectif_anciennete = CategoryField(
        categories=["moins de 10 ans", "entre 10 et 20 ans", "plus de 30 ans"],
        verbose_name="Effectif par anciennet??",
        null=True,
        blank=True,
    )
    effectif_nationalite_francaise = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Effectif de nationalit?? fran??aise",
        null=True,
        blank=True,
    )
    effectif_nationalite_etrangere = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Effectif de nationalit?? ??trang??re",
        null=True,
        blank=True,
    )
    effectif_qualification_detaillee_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="R??partition des hommes",
        help_text="R??partition de l'effectif total masculin au 31/12 selon une structure de qualification d??taill??e",
        null=True,
        blank=True,
    )
    effectif_qualification_detaillee_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="R??partition des femmes",
        help_text="R??partition de l'effectif total f??minin au 31/12 selon une structure de qualification d??taill??e",
        null=True,
        blank=True,
    )

    # inutile car on a consid??t?? la m??me structure du qualification pour la qualification d??taill??e:
    # effectif_cadres = models.IntegerField()
    # effectif_techniciens = models.IntegerField()
    # effectif_agents_de_maitrise = models.IntegerField()
    # effectif_employes_qualifies = models.IntegerField()
    # effectif_employes_non_qualifies = models.IntegerField()
    # effectif_ouvriers_qualifies = models.IntegerField()
    # effectif_ouvriers_non_qualifies = models.IntegerField()
    # 1?? A - a) ii - Travailleurs ext??rieurs
    nombre_travailleurs_exterieurs = models.IntegerField(
        verbose_name="Nombre de travailleurs ext??rieurs",
        help_text="Nombre de salari??s appartenant ?? une entreprise ext??rieure (prestataire de services) dont l???entreprise conna??t le nombre, soit parce qu???il figure dans le contrat sign?? avec l???entreprise ext??rieure, soit parce que ces travailleurs sont inscrits aux effectifs.",
        null=True,
        blank=True,
    )
    nombre_stagiaires = models.IntegerField(
        verbose_name="Nombre de stagiaires",
        help_text="Stages sup??rieurs ?? une semaine.",
        null=True,
        blank=True,
    )
    nombre_moyen_mensuel_salaries_temporaires = models.IntegerField(
        verbose_name="Nombre moyen mensuel de salari??s temporaires",
        help_text="Est consid??r??e comme salari?? temporaire toute personne mise ?? la disposition de l???entreprise, par une entreprise de travail temporaire.",
        null=True,
        blank=True,
    )
    duree_moyenne_contrat_de_travail_temporaire = models.IntegerField(
        verbose_name="Dur??e moyenne des contrats de travail temporaire",
        help_text="En jours",
        null=True,
        blank=True,
    )
    nombre_salaries_de_l_entreprise_detaches = models.IntegerField(
        verbose_name="Nombre de salari??s de l'entreprise d??tach??s",
        null=True,
        blank=True,
    )
    nombre_salaries_detaches_accueillis = models.IntegerField(
        verbose_name="Nombre de salari??s d??tach??s accueillis",
        null=True,
        blank=True,
    )
    # 1?? A - b) Evolution des emplois, notamment, par cat??gorie professionnelle
    # 1?? A - b) i - Embauches
    nombre_embauches_cdi = models.IntegerField(
        verbose_name="Nombre d'embauches par contrats de travail ?? dur??e ind??termin??e",
        null=True,
        blank=True,
    )
    nombre_embauches_cdd = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'embauches par contrats de travail ?? dur??e d??termin??e",
        help_text="dont nombre de contrats de travailleurs saisonniers",
        null=True,
        blank=True,
    )
    nombre_embauches_jeunes = models.IntegerField(
        verbose_name="Nombre d'embauches de salari??s de moins de vingt-cinq ans",
        null=True,
        blank=True,
    )
    # 1?? A - b) ii - D??parts
    total_departs = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Total des d??parts",
        null=True,
        blank=True,
    )
    nombre_demissions = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de d??missions",
        null=True,
        blank=True,
    )
    nombre_licenciements_economiques = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de licenciements pour motif ??conomique",
        help_text="dont d??parts en retraite et pr??retraite",
        null=True,
        blank=True,
    )
    nombre_licenciements_autres = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de licenciements pour d???autres causes",
        null=True,
        blank=True,
    )
    nombre_fin_cdd = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de fins de contrats de travail ?? dur??e d??termin??e",
        null=True,
        blank=True,
    )
    nombre_fin_periode_essai = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de d??parts au cours de la p??riode d???essai",
        help_text="?? ne remplir que si ces d??parts sont comptabilis??s dans le total des d??parts",
        null=True,
        blank=True,
    )
    nombre_mutations = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de mutations d???un ??tablissement ?? un autre",
        null=True,
        blank=True,
    )
    nombre_departs_volontaires_retraite_preretraite = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de d??parts volontaires en retraite et pr??retraite",
        help_text="Distinguer les diff??rents syst??mes l??gaux et conventionnels de toute nature",
        null=True,
        blank=True,
    )
    nombre_deces = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de d??c??s",
        null=True,
        blank=True,
    )
    # 1?? A - b) iii - Promotions
    nombre_promotions = models.IntegerField(
        verbose_name="Nombre de salari??s promus dans l???ann??e dans une cat??gorie sup??rieure",
        help_text="Utiliser les cat??gories de la nomenclature d??taill??e",
        null=True,
        blank=True,
    )
    # 1?? A - b) iv - Ch??mage
    nombre_salaries_chomage_partiel = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s mis en ch??mage partiel pendant l???ann??e consid??r??e",
        null=True,
        blank=True,
    )
    nombre_heures_chomage_partiel_indemnisees = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre total d'heures de ch??mage partiel indemnis??es",
        help_text="Y compris les heures indemnis??es au titre du ch??mage total en cas d???arr??t de plus de quatre semaines cons??cutives",
        null=True,
        blank=True,
    )
    nombre_heures_chomage_partiel_non_indemnisees = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre total d'heures de ch??mage partiel non indemnis??es",
        null=True,
        blank=True,
    )
    nombre_salaries_chomage_intemperies = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s mis en ch??mage intemp??ries",
        null=True,
        blank=True,
    )
    nombre_heures_chomage_intemperies_indemnisees = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre total d'heures de ch??mage intemp??ries indemnis??es",
        null=True,
        blank=True,
    )
    nombre_heures_chomage_intemperies_non_indemnisees = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre total d'heures de ch??mage intemp??ries non indemnis??es",
        null=True,
        blank=True,
    )
    # 1?? A - c) Evolution de l???emploi des personnes handicap??es et mesures prises pour le d??velopper
    nombre_travailleurs_handicap??s = models.IntegerField(
        verbose_name="Nombre de travailleurs handicap??s employ??s sur l'ann??e consid??r??e",
        help_text="tel qu???il r??sulte de la d??claration obligatoire pr??vue ?? l???article L. 5212-5.",
        null=True,
        blank=True,
    )
    nombre_travailleurs_handicapes_accidents_du_travail = models.IntegerField(
        verbose_name="Nombre de travailleurs handicap??s ?? la suite d'accidents du travail intervenus dans l'entreprise",
        help_text="employ??s sur l'ann??e consid??r??e",
        null=True,
        blank=True,
    )
    # 1?? A - d) Evolution du nombre de stagiaires
    # 1?? A - e) Formation professionnelle : investissements en formation, publics concern??s
    # 1?? A - e) i - Formation professionnelle continue
    # Conform??ment aux donn??es relatives aux contributions de formation professionnelle de la d??claration sociale nominative.
    pourcentage_masse_salariale_formation_continue = models.FloatField(
        verbose_name="Pourcentage de la masse salariale aff??rent ?? la formation continue",
        null=True,
        blank=True,
    )
    montant_formation_continue = CategoryField(
        categories=[
            "formation interne",
            "formation effectu??e en application de conventions",
            "versement aux organismes de recouvrement",
            "versement aupr??s d'organismes agr????s",
            "autres",
        ],
        verbose_name="Montant consacr?? ?? la formation continue",
        null=True,
        blank=True,
    )
    nombre_stagiaires_formation_continue_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Nombre de stagiaires hommes",
        null=True,
        blank=True,
    )
    nombre_stagiaires_formation_continue_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Nombre de stagiaires femmes",
        null=True,
        blank=True,
    )
    nombre_heures_stage_remunerees_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Nombre d'heures de stage r??mun??r??es pour les hommes",
        null=True,
        blank=True,
    )
    nombre_heures_stage_remunerees_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Nombre d'heures de stage r??mun??r??es pour les femmes",
        null=True,
        blank=True,
    )
    nombre_heures_stage_non_remunerees_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Nombre d'heures de stage non r??mun??r??es pour les hommes",
        null=True,
        blank=True,
    )
    nombre_heures_stage_non_remunerees_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Nombre d'heures de stage non r??mun??r??es pour les femmes",
        null=True,
        blank=True,
    )
    type_stages = models.TextField(
        verbose_name="D??composition par type de stages",
        help_text="?? titre d'exemple : adaptation, formation professionnelle, entretien ou perfectionnement des connaissances",
        null=True,
        blank=True,
    )
    # 1?? A - e) ii - Cong??s formation
    nombre_salaries_conge_formation_remunere = models.IntegerField(
        verbose_name="Nombre de salari??s ayant b??n??fici?? d'un cong?? formation r??mun??r??",
        null=True,
        blank=True,
    )
    nombre_salaries_conge_formation_non_remunere = models.IntegerField(
        verbose_name="Nombre de salari??s ayant b??n??fici?? d'un cong?? formation non r??mun??r??",
        null=True,
        blank=True,
    )
    nombre_salaries_conge_formation_refuse = models.IntegerField(
        verbose_name="Nombre de salari??s auxquels a ??t?? refus?? un cong?? formation",
        null=True,
        blank=True,
    )
    # 1?? A - e) iii - Apprentissage
    nombre_contrats_apprentissage = models.IntegerField(
        verbose_name="Nombre de contrats d???apprentissage conclus dans l???ann??e",
        null=True,
        blank=True,
    )
    # 1?? A - f) Conditions de travail
    # 1?? A - f) i - Accidents du travail et de trajet
    # taux_frequence_accidents_travail = CategoryField(
    #     verbose_name="Taux de fr??quence des accidents du travail"
    # )
    # nombre_accidents_travail_par_heure_travaillee = models.IntegerField(
    #     verbose_name="Nombre d'accidents avec arr??ts de travail divis?? par nombre d'heures travaill??es"
    # )
    # taux_gravite_accidents_travail = CategoryField(
    #     verbose_name="Taux de gravit?? des accidents du travail"
    # )
    # nombre_journees_perdues_par_heure_travaillee = models.IntegerField(
    #     verbose_name="Nombre des journ??es perdues divis?? par nombre d'heures travaill??es"
    # )
    nombre_incapacites_permanentes_partielles = CategoryField(
        categories=["fran??ais", "??trangers"],
        verbose_name="Nombre d'incapacit??s permanentes partielles notifi??es ?? l'entreprise au cours de l'ann??e consid??r??e",
        null=True,
        blank=True,
    )
    nombre_incapacites_permanentes_totales = CategoryField(
        categories=["fran??ais", "??trangers"],
        verbose_name="Nombre d'incapacit??s permanentes totales notifi??es ?? l'entreprise au cours de l'ann??e consid??r??e",
        null=True,
        blank=True,
    )
    nombre_accidents_travail_mortels = models.IntegerField(
        verbose_name="Nombre d'accidents mortels de travail",
        null=True,
        blank=True,
    )
    nombre_accidents_trajet_mortels = models.IntegerField(
        verbose_name="Nombre d'accidents mortels de trajet",
        null=True,
        blank=True,
    )
    nombre_accidents_trajet_avec_arret_travail = models.IntegerField(
        verbose_name="Nombre d'accidents de trajet ayant entra??n?? un arr??t de travail",
        null=True,
        blank=True,
    )
    nombre_accidents_salaries_temporaires_ou_prestataires = models.IntegerField(
        verbose_name="Nombre d'accidents dont sont victimes les salari??s temporaires ou de prestations de services dans l'entreprise",
        null=True,
        blank=True,
    )
    taux_cotisation_securite_sociale_accidents_travail = models.FloatField(
        verbose_name="Taux de la cotisation s??curit?? sociale d'accidents de travail",
        null=True,
        blank=True,
    )
    montant_cotisation_securite_sociale_accidents_travail = models.IntegerField(
        verbose_name="Montant de la cotisation s??curit?? sociale d'accidents de travail",
        null=True,
        blank=True,
    )

    # 1?? A - f) ii - R??partition des accidents par ??l??ments mat??riels
    # Faire r??f??rence aux codes de classification des ??l??ments mat??riels des accidents (arr??t?? du 10 octobre 1974).
    nombre_accidents_existence_risques_graves = models.IntegerField(
        verbose_name="Nombre d'accidents li??s ?? l'existence de risques grave",
        help_text="Codes 32 ?? 40",
        null=True,
        blank=True,
    )
    nombre_accidents_chutes_d??nivellation = models.IntegerField(
        verbose_name="Nombre d'accidents li??s ?? des chutes avec d??nivellation",
        help_text="Code 02",
        null=True,
        blank=True,
    )
    nombre_accidents_machines = models.IntegerField(
        verbose_name="Nombre d'accidents occasionn??s par des machines",
        help_text="?? l'exception de ceux li??s aux risques ci-dessus, codes 09 ?? 30",
        null=True,
        blank=True,
    )
    nombre_accidents_circulation_manutention_stockage = models.IntegerField(
        verbose_name="Nombre d'accidents de circulation-manutention-stockage",
        help_text="Codes 01, 03, 04 et 06, 07, 08",
        null=True,
        blank=True,
    )
    nombre_accidents_objets_en_mouvement = models.IntegerField(
        verbose_name="Nombre d'accidents occasionn??s par des objets, masses, particules en mouvement accidentel",
        help_text="Code 05",
        null=True,
        blank=True,
    )
    nombre_accidents_autres = models.IntegerField(
        verbose_name="Autres cas",
        null=True,
        blank=True,
    )

    # 1?? A - f) iii - Maladies professionnelles
    nombre_maladies_professionnelles = models.IntegerField(
        verbose_name="Nombre des maladies professionnelles",
        help_text="Nombre des maladies professionnelles d??clar??es ?? la s??curit?? sociale au cours de l'ann??e",
        null=True,
        blank=True,
    )
    denomination_maladies_professionnelles = models.TextField(
        verbose_name="D??nomination des maladies professionnelles",
        help_text="D??nomination des maladies professionnelles d??clar??es ?? la s??curit?? sociale au cours de l'ann??e",
        null=True,
        blank=True,
    )
    nombre_salaries_affections_pathologiques = models.IntegerField(
        verbose_name="Nombre de salari??s atteints par des affections pathologiques ?? caract??re professionnel",
        null=True,
        blank=True,
    )
    caracterisation_affections_pathologiques = models.TextField(
        verbose_name="Caract??risation des affections pathologiques ?? caract??re professionnel",
        null=True,
        blank=True,
    )
    nombre_declaration_procedes_travail_dangereux = models.IntegerField(
        verbose_name="Nombre de d??clarations par l'employeur de proc??d??s de travail susceptibles de provoquer des maladies professionnelles",
        help_text="En application de l'article L. 461-4 du code de la s??curit?? sociale",
        null=True,
        blank=True,
    )

    #     # 1?? A - f) iv - D??penses en mati??re de s??curit??
    effectif_forme_securite = models.IntegerField(
        verbose_name="Effectif form?? ?? la s??curit?? dans l'ann??e",
        null=True,
        blank=True,
    )
    montant_depenses_formation_securite = models.IntegerField(
        verbose_name="Montant des d??penses de formation ?? la s??curit?? r??alis??es dans l'entreprise",
        null=True,
        blank=True,
    )
    taux_realisation_programme_securite = models.IntegerField(
        verbose_name="Taux de r??alisation du programme de s??curit?? pr??sent?? l'ann??e pr??c??dente",
        null=True,
        blank=True,
    )
    nombre_plans_specifiques_securite = models.IntegerField(
        verbose_name="Nombre de plans sp??cifiques de s??curit??",
        null=True,
        blank=True,
    )
    # 1?? A - f) v - Dur??e et am??nagement du temps de travail
    horaire_hebdomadaire_moyen = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Horaire hebdomadaire moyen affich?? des ouvriers et employ??s ou cat??gories assimil??es",
        help_text="Il est possible de remplacer cet indicateur par la somme des heures travaill??es durant l'ann??e.",
        null=True,
        blank=True,
    )
    nombre_salaries_repos_compensateur_code_travail = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s ayant b??n??fici?? d'un repos compensateur au titre du code du travail",
        help_text="Au sens des dispositions du code du travail et du code rural et de la p??che maritime instituant un repos compensateur en mati??re d'heures suppl??mentaires.",
        null=True,
        blank=True,
    )
    nombre_salaries_repos_compensateur_regime_conventionne = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s ayant b??n??fici?? d'un repos compensateur au titre d'un r??gime conventionne",
        null=True,
        blank=True,
    )
    nombre_salaries_horaires_individualises = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s b??n??ficiant d'un syst??me d'horaires individualis??s",
        help_text="Au sens de l'article L. 3121-48.",
        null=True,
        blank=True,
    )
    nombre_salaries_temps_partiel_20_30_heures = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s employ??s ?? temps partiel entre 20 et 30 heures (33)",
        help_text="Au sens de l'article L. 3123-1.",
        null=True,
        blank=True,
    )
    nombre_salaries_temps_partiel_autres = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s employ??s sous d'autres formes de temps partiel",
        null=True,
        blank=True,
    )
    nombre_salaries_2_jours_repos_hebdomadaire_consecutifs = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s ayant b??n??fici?? tout au long de l'ann??e consid??r??e de deux jours de repos hebdomadaire cons??cutifs",
        null=True,
        blank=True,
    )
    nombre_moyen_jours_conges_annuels = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre moyen de jours de cong??s annuels (non compris le repos compensateur)",
        help_text="Repos compensateur non compris. Cet indicateur peut ??tre calcul?? sur la derni??re p??riode de r??f??rence.",
        null=True,
        blank=True,
    )
    nombre_jours_feries_payes = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de jours f??ri??s pay??s",
        null=True,
        blank=True,
    )
    # 1?? A - f) vi - Absent??isme
    # Possibilit??s de comptabiliser tous les indicateurs de la rubrique absent??isme, au choix, en journ??es, 1/2 journ??es ou heures.
    UNITE_ABSENTEISME_CHOICES = [
        ("J", "Journ??es"),
        ("1/2J", "1/2 journ??es"),
        ("H", "Heures"),
    ]
    unite_absenteisme = models.CharField(
        max_length=10,
        choices=UNITE_ABSENTEISME_CHOICES,
        default="J",
    )
    nombre_unites_absence = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de journ??es d'absence",
        help_text="Ne sont pas compt??s parmi les absences : les diverses sortes de cong??s, les conflits et le service national.",
        null=True,
        blank=True,
    )
    nombre_unites_theoriques_travaillees = models.IntegerField(
        verbose_name="Nombre de journ??es th??oriques travaill??es",
        null=True,
        blank=True,
    )
    nombre_unites_absence_maladie = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de journ??es d'absence pour maladie",
        null=True,
        blank=True,
    )
    nombre_unites_absence_maladie_par_duree = CategoryField(
        categories=["< 3 jours", "de 3 ?? 90 jours", "> 90 jours"],
        verbose_name="R??partition des absences pour maladie selon leur dur??e",
        null=True,
        blank=True,
    )
    nombre_unites_absence_accidents = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de journ??es d'absence pour accidents du travail et de trajet ou maladies professionnelles",
        null=True,
        blank=True,
    )
    nombre_unites_absence_maternite = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de journ??es d'absence pour maternit??",
        null=True,
        blank=True,
    )
    nombre_unites_absence_conges_autorises = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de journ??es d'absence pour cong??s autoris??s",
        help_text="(??v??nements familiaux, cong??s sp??ciaux pour les femmes ???)",
        null=True,
        blank=True,
    )
    nombre_unites_absence_autres = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de journ??es d'absence imputables ?? d'autres causes",
        null=True,
        blank=True,
    )
    # 1?? A - f) vii - Organisation et contenu du travail
    nombre_personnes_horaires_alternant_ou_nuit = models.IntegerField(
        verbose_name="Nombre de personnes occupant des emplois ?? horaires alternant ou de nuit",
        null=True,
        blank=True,
    )
    nombre_personnes_horaires_alternant_ou_nuit_50_ans = models.IntegerField(
        verbose_name="Nombre de personnes occupant des emplois ?? horaires alternant ou de nuit de plus de cinquante ans",
        null=True,
        blank=True,
    )
    nombre_taches_repetitives = CategoryField(
        categories=["hommes", "femmes"],
        verbose_name="Nombre de salari??(e)s affect??s ?? des t??ches r??p??titives",
        help_text="Au sens de l'article D. 4163-2",
        null=True,
        blank=True,
    )
    # 1?? A - f) viii - Conditions physiques de travail
    nombre_personnes_exposees_bruit = models.IntegerField(
        verbose_name="Nombre de personnes expos??es de fa??on habituelle et r??guli??re ?? plus de 80 ?? 85 db ?? leur poste de travail",
        help_text="Les valeurs limites d'exposition et les valeurs d'exposition d??clenchant une action de pr??vention qui sont fix??es dans le tableau pr??vu ?? l'article R. 4431-2.",
        null=True,
        blank=True,
    )
    nombre_salaries_exposes_temperatures = models.IntegerField(
        verbose_name="Nombre de salari??s expos??s au froid et ?? la chaleur",
        help_text="Au sens des articles R. 4223-13 ?? R. 4223-15",
        null=True,
        blank=True,
    )
    nombre_salaries_exposes_temperatures_extremes = models.IntegerField(
        verbose_name="Nombre de salari??s expos??s aux temp??ratures extr??mes",
        help_text="Au sens de l'article D. 4163-2 : temp??rature inf??rieure ou ??gale ?? 5 degr??s Celsius ou au moins ??gale ?? 30 degr??s Celsius pour minimum 900 heures par an.",
        null=True,
        blank=True,
    )
    nombre_salaries_exposes_intemperies = models.IntegerField(
        verbose_name="Nombre de salari??s travaillant aux intemp??ries de fa??on habituelle et r??guli??re",
        help_text="Au sens de l'article L. 5424-8 : Sont consid??r??es comme intemp??ries, les conditions atmosph??riques et les inondations lorsqu'elles rendent dangereux ou impossible l'accomplissement du travail eu ??gard soit ?? la sant?? ou ?? la s??curit?? des salari??s, soit ?? la nature ou ?? la technique du travail ?? accomplir.",
        null=True,
        blank=True,
    )
    nombre_analyses_produits_toxiques = models.IntegerField(
        verbose_name="Nombre de pr??l??vements, d'analyses de produits toxiques et mesures",
        help_text="Renseignements tir??s du rapport du directeur du service de pr??vention et de sant?? au travail interentreprises",
        null=True,
        blank=True,
    )
    # 1?? A - f) ix - Transformation de l???organisation du travail
    experiences_transformation_organisation_travail = models.TextField(
        verbose_name="Exp??riences de transformation de l'organisation du travail en vue d'en am??liorer le contenu",
        help_text="Pour l'explication de ces exp??riences d'am??lioration du contenu du travail, donner le nombre de salari??s concern??s.",
        null=True,
        blank=True,
    )
    # 1?? A - f) x - D??penses d???am??lioration de conditions de travail
    montant_depenses_amelioration_conditions_travail = models.IntegerField(
        verbose_name="Montant des d??penses consacr??es ?? l'am??lioration des conditions de travail dans l'entreprise",
        help_text="Non compris l'??valuation des d??penses en mati??re de sant?? et de s??curit??.",
        null=True,
        blank=True,
    )
    taux_realisation_programme_amelioration_conditions_travail = models.IntegerField(
        verbose_name="Taux de r??alisation du programme d'am??lioration des conditions de travail dans l'entreprise l'ann??e pr??c??dente",
        null=True,
        blank=True,
    )
    # 1?? A - f) xi - M??decine du travail
    # Renseignements tir??s du rapport du directeur du service de pr??vention et de sant?? au travail interentreprises.
    nombre_visites_medicales = CategoryField(
        categories=["suivi de droit commun", "suivi individuel renforc??"],
        verbose_name="Nombre de visites d'information et de pr??vention des travailleurs",
        help_text="Selon le type de suivi",
        null=True,
        blank=True,
    )
    nombre_examens_medicaux = CategoryField(
        categories=["suivi de droit commun", "suivi individuel renforc??"],
        verbose_name="Nombre d'examens m??dicaux des travailleurs",
        null=True,
        blank=True,
    )
    nombre_examens_medicaux_complementaires = CategoryField(
        categories=["soumis ?? surveillance", "autres"],
        verbose_name="Nombre d'examens m??dicaux compl??mentaires des travailleurs",
        null=True,
        blank=True,
    )
    pourcentage_temps_medecin_du_travail = CategoryField(
        categories=["analyse", "intervention"],
        verbose_name="Part du temps consacr?? par le m??decin du travail en milieu de travail",
        null=True,
        blank=True,
    )
    # 1?? A - f) xii - Travailleurs inaptes
    nombre_salaries_inaptes = models.IntegerField(
        verbose_name="Nombre de salari??s inaptes",
        help_text="Nombre de salari??s d??clar??s d??finitivement inaptes ?? leur emploi par le m??decin du travail",
        null=True,
        blank=True,
    )
    nombre_salaries_reclasses = models.IntegerField(
        verbose_name="Nombre de salari??s reclass??s",
        help_text="Nombre de salari??s reclass??s dans l'entreprise ?? la suite d'une inaptitude",
        null=True,
        blank=True,
    )
    # 1?? B - Investissement mat??riel et immat??riel
    # 1?? B - a) Evolution des actifs nets d???amortissement et de d??pr??ciations ??ventuelles (immobilisations)
    evolution_amortissement = models.TextField(
        verbose_name="Evolution des actifs nets d???amortissement et de d??pr??ciations ??ventuelles (immobilisations)",
        null=True,
        blank=True,
    )
    # 1?? B - b) Le cas ??ch??ant, d??penses de recherche et d??veloppement
    montant_depenses_recherche_developpement = models.IntegerField(
        verbose_name="D??penses de recherche et d??veloppement",
        null=True,
        blank=True,
    )
    # 1?? B - c) L?????volution de la productivit?? et le taux d???utilisation des capacit??s de production, lorsque ces ??l??ments sont mesurables dans l???entreprise
    evolution_productivite = models.TextField(
        verbose_name="Evolution de la productivit?? et le taux d???utilisation des capacit??s de production",
        help_text="lorsque ces ??l??ments sont mesurables dans l???entreprise",
        null=True,
        blank=True,
    )

    ###########################################################

    # 2?? Egalit?? professionnelle entre les femmes et les hommes au sein de l'entreprise
    #   I. Indicateurs sur la situation compar??e des femmes et des hommes dans l'entreprise
    #     A-Conditions g??n??rales d'emploi
    #       a) Effectifs : Donn??es chiffr??es par sexe
    nombre_CDI_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'hommes en CDI",
        null=True,
        blank=True,
    )
    nombre_CDI_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de femmes en CDI",
        null=True,
        blank=True,
    )
    nombre_CDD_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'hommes en CDD",
        null=True,
        blank=True,
    )
    nombre_CDD_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de femmes en CDD",
        null=True,
        blank=True,
    )
    #       b) Dur??e et organisation du travail: Donn??es chiffr??es par sexe
    effectif_par_duree_homme = CategoryField(
        categories=[
            "temps complet",
            "temps partiel entre 20 et 30 heures",
            "autres temps partiels",
        ],
        verbose_name="R??partition des effectifs hommes selon la dur??e du travail",
        null=True,
        blank=True,
    )
    effectif_par_duree_femme = CategoryField(
        categories=[
            "temps complet",
            "temps partiel entre 20 et 30 heures",
            "autres temps partiels",
        ],
        verbose_name="R??partition des effectifs femmes selon la dur??e du travail",
        null=True,
        blank=True,
    )
    effectif_par_organisation_du_travail_homme = CategoryField(
        categories=[
            "travail post??",
            "travail de nuit",
            "horaires variables",
            "travail atypique dont travail durant le week-end",
        ],
        verbose_name="R??partition des effectifs hommes selon l'organisation du travail",
        null=True,
        blank=True,
    )
    effectif_par_organisation_du_travail_femme = CategoryField(
        categories=[
            "travail post??",
            "travail de nuit",
            "horaires variables",
            "travail atypique dont travail durant le week-end",
        ],
        verbose_name="R??partition des effectifs femmes selon l'organisation du travail",
        null=True,
        blank=True,
    )
    #       c) Donn??es sur les cong??s
    conges_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="R??partition des cong??s des hommes",
        null=True,
        blank=True,
    )
    conges_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="R??partition des cong??s des femmes",
        null=True,
        blank=True,
    )
    conges_par_type_homme = CategoryField(
        categories=["compte ??pargne-temps", "cong?? parental", "cong?? sabbatique"],
        verbose_name="R??partition des cong??s des hommes selon le type de cong??s dont la dur??e est sup??rieure ?? six mois",
        null=True,
        blank=True,
    )
    conges_par_type_femme = CategoryField(
        categories=["compte ??pargne-temps", "cong?? parental", "cong?? sabbatique"],
        verbose_name="R??partition des cong??s des femmes selon le type de cong??s dont la dur??e est sup??rieure ?? six mois",
        null=True,
        blank=True,
    )
    #      d) Donn??es sur les embauches et les d??parts
    embauches_CDI_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="R??partition des embauches hommes en CDI par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    embauches_CDI_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="R??partition des embauches femmes en CDI par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    embauches_CDD_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="R??partition des embauches hommes en CDD par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    embauches_CDD_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="R??partition des embauches femmes en CDD par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    departs_retraite_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'hommes partis en retraite",
        null=True,
        blank=True,
    )
    departs_demission_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'hommes ayant d??missionn??",
        null=True,
        blank=True,
    )
    departs_fin_CDD_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'hommes en fin de CDD",
        null=True,
        blank=True,
    )
    departs_licenciement_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'hommes licenci??s",
        null=True,
        blank=True,
    )
    departs_retraite_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de femmes parties en retraite",
        null=True,
        blank=True,
    )
    departs_demission_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de femmes ayant d??missionn??",
        null=True,
        blank=True,
    )
    departs_fin_CDD_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de femmes en fin de CDD",
        null=True,
        blank=True,
    )
    departs_licenciement_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de femmes licenci??es",
        null=True,
        blank=True,
    )
    #      e) Positionnement dans l'entreprise
    # r??partition des effectifs par cat??gorie professionnelle : d??duisible de a)
    # r??partition des effectifs par niveau ou coefficient hi??rarchique : quels sont les niveaux/coeff ?
    #     B - R??mun??rations et d??roulement de carri??re
    #        a) Promotion
    nombre_promotions_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de promotions homme",
        null=True,
        blank=True,
    )
    nombre_promotions_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de promotions femme",
        null=True,
        blank=True,
    )
    duree_moyenne_entre_deux_promotions_homme = models.IntegerField(
        verbose_name="Dur??e moyenne entre deux promotions pour les hommes",
        null=True,
        blank=True,
    )
    duree_moyenne_entre_deux_promotions_femme = models.IntegerField(
        verbose_name="Dur??e moyenne entre deux promotions pour les femmes",
        null=True,
        blank=True,
    )
    #        b) Anciennet??
    anciennete_moyenne_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Anciennet?? moyenne des hommes par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    anciennete_moyenne_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Anciennet?? moyenne des femmes par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    anciennete_moyenne_dans_categorie_profesionnelle_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Anciennet?? moyenne des hommes dans chaque cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    anciennete_moyenne_dans_categorie_profesionnelle_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Anciennet?? moyenne des femmes dans chaque cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    # anciennet?? moyenne par/dans niveau ou coefficient hi??rarchique : quels sont les niveaux/coeff ?
    #        c) Age
    age_moyen_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Age moyen des hommes par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    age_moyen_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Age moyen des femmes par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    # ??ge moyen par niveau ou coefficient hi??rarchique : quels sont les niveaux/coeff ?
    #        d) R??mun??rations
    REMUNERATIONS_CHOICES = [
        ("moyenne", "R??mun??ration moyenne"),
        ("mediane", "R??mun??ration m??diane"),
    ]
    remuneration_moyenne_ou_mediane = models.CharField(
        verbose_name="R??mun??ration moyenne ou m??diane",
        help_text="Les indicateurs suivants peuvent ??tre renseign??s au choix en r??mun??ration moyenne ou r??mun??ration m??diane",
        max_length=10,
        choices=REMUNERATIONS_CHOICES,
        default="moyenne",
    )
    remuneration_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="R??mun??ration moyenne/m??diane mensuelle des hommes par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    remuneration_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="R??mun??ration moyenne/m??diane mensuelle des femmes par cat??gorie professionnelle",
        null=True,
        blank=True,
    )
    # r??mun??ration moyenne ou m??diane mensuelle par niveau ou coefficient hi??rarchique : quels sont les niveaux/coeff ?
    # Cet indicateur n'a pas ?? ??tre renseign?? lorsque sa mention est de nature ?? porter atteinte ?? la confidentialit?? des donn??es correspondantes, compte tenu notamment du nombre r??duit d'individus dans un niveau ou coefficient hi??rarchique
    remuneration_par_age_homme = CategoryField(
        categories=["moins de 30 ans", "30 ?? 39 ans", "40 ?? 49 ans", "50 ans et plus"],
        verbose_name="R??mun??ration moyenne/mediane mensuelle des hommes par tranche d'??ge",
        null=True,
        blank=True,
    )
    remuneration_par_age_femme = CategoryField(
        categories=["moins de 30 ans", "30 ?? 39 ans", "40 ?? 49 ans", "50 ans et plus"],
        verbose_name="R??mun??ration moyenne/m??diane mensuelle des femmes par tranche d'??ge",
        null=True,
        blank=True,
    )
    nombre_femmes_plus_hautes_remunerations = models.IntegerField(
        verbose_name="Nombre de femmes dans les dix plus hautes r??mun??rations",
        null=True,
        blank=True,
    )
    #     C - Formation
    nombre_moyen_heures_formation_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre moyen d'heures d'actions de formation par salari?? et par an",
        help_text="hommes",
        null=True,
        blank=True,
    )
    nombre_moyen_heures_formation_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre moyen d'heures d'actions de formation par salari??e et par an",
        help_text="femmes",
        null=True,
        blank=True,
    )
    action_adaptation_au_poste_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'hommes ayant suivi une formation d'adaptation au poste",
        null=True,
        blank=True,
    )
    action_adaptation_au_poste_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de femmes ayant suivi une formation d'adaptation au poste",
        null=True,
        blank=True,
    )
    action_maintien_emploi_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'hommes ayant suivi une formation pour le maintien dans l'emploi",
        null=True,
        blank=True,
    )
    action_maintien_emploi_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de femmes ayant suivi une formation pour le maintien dans l'emploi",
        null=True,
        blank=True,
    )
    action_developpement_competences_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre d'hommes ayant suivi une formation pour le d??veloppement des comp??tences",
        null=True,
        blank=True,
    )
    action_developpement_competences_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de femmes ayant suivi une formation pour le d??veloppement des comp??tences",
        null=True,
        blank=True,
    )
    #     D - Conditions de travail, sant?? et s??curit?? au travail
    exposition_risques_pro_homme = CategoryField(
        categories=[
            "manutentions manuelles de charges",
            "postures p??nibles",
            "vibrations m??caniques",
            "agents chimiques dangereux",
            "milieu hyperbare",
            "temp??ratures extr??mes",
            "bruit",
            "travail de nuit",
            "travail en ??quipes successives alternantes",
            "travail r??p??titif",
        ],
        verbose_name="R??partition des postes de travail expos??s ?? des risques professionnels occup??s par des hommes",
        null=True,
        blank=True,
    )
    exposition_risques_pro_femme = CategoryField(
        categories=[
            "manutentions manuelles de charges",
            "postures p??nibles",
            "vibrations m??caniques",
            "agents chimiques dangereux",
            "milieu hyperbare",
            "temp??ratures extr??mes",
            "bruit",
            "travail de nuit",
            "travail en ??quipes successives alternantes",
            "travail r??p??titif",
        ],
        verbose_name="R??partition des postes de travail expos??s ?? des risques professionnels occup??s par des femmes",
        null=True,
        blank=True,
    )
    accidents_homme = CategoryField(
        categories=[
            "accidents de travail",
            "accidents de trajet",
            "maladies professionnelles",
        ],
        verbose_name="Accidents de travail, accidents de trajet et maladies professionnelles chez les hommes",
        null=True,
        blank=True,
    )
    accidents_femme = CategoryField(
        categories=[
            "accidents de travail",
            "accidents de trajet",
            "maladies professionnelles",
        ],
        verbose_name="Accidents de travail, accidents de trajet et maladies professionnelles chez les femmes",
        null=True,
        blank=True,
    )
    nombre_accidents_travail_avec_arret_homme = models.IntegerField(
        verbose_name="Nombre d'accidents de travail ayant entra??n?? un arr??t de travail chez les hommes",
        null=True,
        blank=True,
    )
    nombre_accidents_travail_avec_arret_femme = models.IntegerField(
        verbose_name="Nombre d'accidents de travail ayant entra??n?? un arr??t de travail chez les femmes",
        null=True,
        blank=True,
    )
    nombre_accidents_trajet_avec_arret_homme = models.IntegerField(
        verbose_name="Nombre d'accidents de trajet ayant entra??n?? un arr??t de travail chez les hommes",
        null=True,
        blank=True,
    )
    nombre_accidents_trajet_avec_arret_femme = models.IntegerField(
        verbose_name="Nombre d'accidents de trajet ayant entra??n?? un arr??t de travail chez les hommes",
        null=True,
        blank=True,
    )
    nombre_accidents_par_elements_materiels_homme = models.TextField(
        verbose_name="R??partition des accidents par ??l??ments mat??riels chez les hommes",
        help_text="Faire r??f??rence aux codes de classification des ??l??ments mat??riels des accidents (arr??t?? du 10 octobre 1974).",
        null=True,
        blank=True,
    )
    nombre_accidents_par_elements_materiels_femme = models.TextField(
        verbose_name="R??partition des accidents par ??l??ments mat??riels chez les hommes",
        help_text="Faire r??f??rence aux codes de classification des ??l??ments mat??riels des accidents (arr??t?? du 10 octobre 1974).",
        null=True,
        blank=True,
    )
    nombre_et_denominations_maladies_pro_homme = models.TextField(
        verbose_name="Nombre et d??nomination des maladies professionnelles d??clar??es ?? la S??curit?? sociale au cours de l'ann??e concernant les hommes",
        null=True,
        blank=True,
    )
    nombre_et_denominations_maladies_pro_femme = models.TextField(
        verbose_name="Nombre et d??nomination des maladies professionnelles d??clar??es ?? la S??curit?? sociale au cours de l'ann??e concernant les femmes",
        null=True,
        blank=True,
    )
    nombre_journees_absence_accident_homme = models.IntegerField(
        verbose_name="Nombre de journ??e d'absence pour accidents de travail, accidents de trajet ou maladies professionnelles chez les hommes",
        null=True,
        blank=True,
    )
    nombre_journees_absence_accident_femme = models.IntegerField(
        verbose_name="Nombre de journ??e d'absence pour accidents de travail, accidents de trajet ou maladies professionnelles chez les femmes",
        null=True,
        blank=True,
    )
    maladies_homme = CategoryField(
        categories=["nombre d'arr??ts de travail", "nombre de journ??es d'absence"],
        verbose_name="Maladies chez les hommes",
        null=True,
        blank=True,
    )
    maladies_femme = CategoryField(
        categories=["nombre d'arr??ts de travail", "nombre de journ??es d'absence"],
        verbose_name="Maladies chez les femmes",
        null=True,
        blank=True,
    )
    maladies_avec_examen_de_reprise_homme = CategoryField(
        categories=["nombre d'arr??ts de travail", "nombre de journ??es d'absence"],
        verbose_name="Maladies ayant donn?? lieu ?? un examen de reprise du travail chez les hommes",
        help_text="en application du 3?? de l'article R. 4624-31",
        null=True,
        blank=True,
    )
    maladies_avec_examen_de_reprise_femme = CategoryField(
        categories=["nombre d'arr??ts de travail", "nombre de journ??es d'absence"],
        verbose_name="Maladies ayant donn?? lieu ?? un examen de reprise du travail chez les femmes",
        help_text="en application du 3?? de l'article R. 4624-31",
        null=True,
        blank=True,
    )
    #   II. Indicateurs relatifs ?? l'articulation entre l'activit?? professionnelle et l'exercice de la responsabilit?? familiale
    #      A. Cong??s
    complement_salaire_conge_paternite = models.BooleanField(
        verbose_name="Compl??ment de salaire pour le cong?? de paternit??",
        help_text="Existence d'un compl??ment de salaire vers?? par l'employeur pour le cong?? de paternit??",
        default=False,
    )
    complement_salaire_conge_maternite = models.BooleanField(
        verbose_name="Compl??ment de salaire pour le cong?? de maternit??",
        help_text="Existence d'un compl??ment de salaire vers?? par l'employeur pour le cong?? de maternit??",
        default=False,
    )
    complement_salaire_conge_adoption = models.BooleanField(
        verbose_name="Compl??ment de salaire pour le cong?? d'adoption",
        help_text="Existence d'un compl??ment de salaire vers?? par l'employeur pour le cong?? d'adoption",
        default=False,
    )
    nombre_jours_conges_paternite_pris = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Jours de cong??s parternit??",
        help_text="Nombre de jours de cong??s de paternit?? pris par le salari?? par rapport au nombre de jours de cong??s th??oriques",
        null=True,
        blank=True,
    )
    #      B-Organisation du temps de travail dans l'entreprise
    existence_orga_facilitant_vie_familiale_et_professionnelle = models.TextField(
        verbose_name="Existence de formules d'organisation du travail facilitant l'articulation de la vie familiale et de la vie professionnelle",
        null=True,
        blank=True,
    )
    nombre_salaries_temps_partiel_choisi_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s homme ayant acc??d?? au temps partiel choisi",
        null=True,
        blank=True,
    )
    nombre_salaries_temps_partiel_choisi_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??es femme ayant acc??d?? au temps partiel choisi",
        null=True,
        blank=True,
    )
    nombre_salaries_temps_partiel_choisi_vers_temps_plein_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??s homme ?? temps partiel choisi ayant repris un travail ?? temps plein",
        null=True,
        blank=True,
    )
    nombre_salaries_temps_partiel_choisi_vers_temps_plein_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Nombre de salari??es femme ?? temps partiel choisi ayant repris un travail ?? temps plein",
        null=True,
        blank=True,
    )
    participation_accueil_petite_enfance = models.BooleanField(
        verbose_name="Participation de l'entreprise et du comit?? social et ??conomique aux modes d'accueil de la petite enfance",
        default=False,
    )
    evolution_depenses_credit_impot_famille = models.TextField(
        verbose_name="Evolution des d??penses ??ligibles au cr??dit d'imp??t famille",
        null=True,
        blank=True,
    )
    #  III. Strat??gie d'action
    mesures_prises_egalite = models.TextField(
        verbose_name="Mesures prises au cours de l'ann??e ??coul??e en vue d'assurer l'??galit?? professionnelle",
        help_text="Bilan des actions de l'ann??e ??coul??e et, le cas ??ch??ant, de l'ann??e pr??c??dente. Evaluation du niveau de r??alisation des objectifs sur la base des indicateurs retenus. Explications sur les actions pr??vues non r??alis??es",
        null=True,
        blank=True,
    )
    objectifs_progression = models.TextField(
        verbose_name="Objectifs de progression pour l'ann??e ?? venir et indicateurs associ??s",
        help_text="D??finition qualitative et quantitative des mesures permettant de les atteindre conform??ment ?? l'article R. 2242-2. Evaluation de leur co??t. Ech??ancier des mesures pr??vues",
        null=True,
        blank=True,
    )

    ###########################################################

    # 3?? Fonds propres, endettement et imp??ts
    capitaux_propres = models.IntegerField(
        verbose_name="Capitaux propres de l'entreprise",
        null=True,
        blank=True,
    )
    emprunts_et_dettes_financieres = models.IntegerField(
        verbose_name="Emprunts et dettes financi??res dont ??ch??ances et charges financi??res",
        null=True,
        blank=True,
    )
    impots_et_taxes = models.IntegerField(
        null=True,
        blank=True,
    )

    # 4?? R??mun??ration des salari??s et dirigeants, dans l'ensemble de leurs ??l??ments
    #   A-Evolution des r??mun??rations salariales
    #     a) Frais de personnel

    frais_personnel = models.IntegerField(
        verbose_name="Frais de personnel, y compris cotisations sociales",
        null=True,
        blank=True,
    )
    evolution_salariale_par_categorie = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        null=True,
        blank=True,
    )
    evolution_salariale_par_sexe = CategoryField(
        categories=["homme", "femme"],
        null=True,
        blank=True,
    )
    salaire_base_minimum_par_categorie = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Salaire de base minimum par cat??gorie",
        null=True,
        blank=True,
    )
    salaire_base_minimum_par_sexe = CategoryField(
        categories=["homme", "femme"],
        verbose_name="Salaire de base minimum par sexe",
        null=True,
        blank=True,
    )
    salaire_moyen_par_categorie = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Salaire moyen par cat??gorie",
        null=True,
        blank=True,
    )
    salaire_moyen_par_sexe = CategoryField(
        categories=["homme", "femme"],
        null=True,
        blank=True,
    )
    salaire_median_par_categorie = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Salaire m??dian par cat??gorie",
        null=True,
        blank=True,
    )
    salaire_median_par_sexe = CategoryField(
        verbose_name="Salaire m??dian par sexe",
        categories=["homme", "femme"],
        null=True,
        blank=True,
    )

    #       i. Montant des r??mun??rations
    rapport_masse_salariale_effectif_mensuel_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Rapport entre la masse salariale annuelle et l'effectif mensuel moyen (hommes)",
        help_text="Masse salariale annuelle totale, au sens de la d??claration annuelle de salaire",
        null=True,
        blank=True,
    )
    rapport_masse_salariale_effectif_mensuel_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Rapport entre la masse salariale annuelle et l'effectif mensuel moyen (femmes)",
        help_text="Masse salariale annuelle totale, au sens de la d??claration annuelle de salaire",
        null=True,
        blank=True,
    )
    remuneration_moyenne_decembre_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="R??mun??ration moyenne du mois de d??cembre (effectif permanent) hors primes ?? p??riodicit?? non mensuelle (hommes)",
        help_text="base 35 heures",
        null=True,
        blank=True,
    )
    remuneration_moyenne_decembre_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="R??mun??ration moyenne du mois de d??cembre (effectif permanent) hors primes ?? p??riodicit?? non mensuelle (femmes)",
        help_text="base 35 heures",
        null=True,
        blank=True,
    )
    remuneration_mensuelle_moyenne_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="R??mun??ration mensuelle moyenne (hommes)",
        null=True,
        blank=True,
    )
    remuneration_mensuelle_moyenne_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="R??mun??ration mensuelle moyenne (femmes)",
        null=True,
        blank=True,
    )
    part_primes_non_mensuelle_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Part des primes ?? p??riodicit?? non mensuelle dans la d??claration de salaire (hommes)",
        null=True,
        blank=True,
    )
    part_primes_non_mensuelle_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE_DETAILLEE,
        verbose_name="Part des primes ?? p??riodicit?? non mensuelle dans la d??claration de salaire (femmes)",
        null=True,
        blank=True,
    )
    remunerations = models.TextField(
        verbose_name="Grille des r??mun??rations",
        help_text="Faire une grille des r??mun??rations en distinguant au moins six tranches.",
        null=True,
        blank=True,
    )

    #       ii. Hi??rarchie des r??mun??rations
    rapport_moyenne_deciles = models.IntegerField(
        verbose_name="rapport entre la moyenne des r??mun??rations des 10 % des salari??s touchant les r??mun??rations les plus ??lev??es et celle correspondant au 10 % des salari??s touchant les r??mun??rations les moins ??lev??es",
        null=True,
        blank=True,
    )
    rapport_moyenne_cadres_ouvriers = models.IntegerField(
        verbose_name="Rapport entre la moyenne des r??mun??rations des cadres ou assimil??s (y compris cadres sup??rieurs et dirigeants) et la moyenne des r??mun??rations des ouvriers non qualifi??s ou assimil??s.",
        help_text="Pour ??tre prises en compte, les cat??gories concern??es doivent comporter au minimum dix salari??s.",
        null=True,
        blank=True,
    )
    montant_10_remunerations_les_plus_eleves = models.IntegerField(
        verbose_name="Montant global des dix r??mun??rations les plus ??lev??es.",
        null=True,
        blank=True,
    )

    #       iii. Mode de calcul des r??mun??rations
    pourcentage_salaries_primes_de_rendement = CategoryField(
        categories=["primes individuelles", "primes collectives"],
        verbose_name="Pourcentage des salari??s dont le salaire d??pend, en tout ou partie, du rendement",
        null=True,
        blank=True,
    )
    pourcentage_ouvriers_employes_payes_au_mois = models.IntegerField(
        verbose_name="Pourcentage des ouvriers et employ??s pay??s au mois sur la base de l'horaire affich??",
        null=True,
        blank=True,
    )  # TODO: remplacer le pourcentage par une valeur absolue ?

    #       iv. Charge salariale globale
    charge_salariale_globale = models.IntegerField(
        null=True,
        blank=True,
    )

    #     b) Pour les entreprises soumises aux dispositions de l'article L. 225-115 du code de commerce, montant global des r??mun??rations vis??es au 4?? de cet article
    montant_global_hautes_remunerations = models.IntegerField(
        verbose_name="Montant global des hautes r??mun??rations",
        help_text="Montant global, certifi?? exact par les commissaires aux comptes, s'il en existe, des r??mun??rations vers??es aux personnes les mieux r??mun??r??es, le nombre de ces personnes ??tant de dix ou de cinq selon que l'effectif du personnel exc??de ou non deux cents salari??s ; uniquement pour les entreprises soumises aux dispositions de l'article L. 225-115 du code de commerce",
        null=True,
        blank=True,
    )

    # B. Epargne salariale : int??ressement, participation
    montant_global_reserve_de_participation = models.IntegerField(
        verbose_name="Montant global de la r??serve de participation",
        help_text="Le montant global de la r??serve de participation est le montant de la r??serve d??gag??e-ou de la provision constitu??e-au titre de la participation sur les r??sultats de l'exercice consid??r??.",
        null=True,
        blank=True,
    )
    montant_moyen_participation = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Montant moyen de la participation et/ ou de l'int??ressement par salari?? b??n??ficiaire",
        help_text="La participation est envisag??e ici au sens du titre II du livre III de la partie III.",
        null=True,
        blank=True,
    )
    part_capital_detenu_par_salaries = models.IntegerField(
        verbose_name="Part du capital d??tenu par les salari??s (dirigeants exclus) gr??ce ?? un syst??me de participation",
        help_text="syst??me de participation??: participation aux r??sultats, int??ressement, actionnariat ???",
        null=True,
        blank=True,
    )

    # C-R??mun??rations accessoires : primes par sexe et par cat??gorie professionnelle, avantages en nature, r??gimes de pr??voyance et de retraite compl??mentaire
    avantages_sociaux = models.TextField(
        verbose_name="Avantages sociaux dans l'entreprise : pour chaque avantage pr??ciser le niveau de garantie pour les cat??gories retenues pour les effectifs",
        null=True,
        blank=True,
    )

    # D-R??mun??ration des dirigeants mandataires sociaux
    remuneration_dirigeants_mandataires_sociaux = models.IntegerField(
        verbose_name="R??mun??ration des dirigeants mandataires sociaux",
        null=True,
        blank=True,
    )

    # 5?? Repr??sentation du personnel et Activit??s sociales et culturelles
    #   A-Repr??sentation du personnel
    #     a) Repr??sentants du personnel et d??l??gu??s syndicaux

    composition_CSE_etablissement = models.TextField(
        verbose_name="Composition des comit??s sociaux et ??conomiques et/ ou d'??tablissement avec indication, s'il y a lieu, de l'appartenance syndicale",
        null=True,
        blank=True,
    )
    participation_elections = models.TextField(
        verbose_name="Participation aux ??lections (par coll??ge) par cat??gories de repr??sentants du personnel",
        null=True,
        blank=True,
    )
    volume_credit_heures = models.IntegerField(
        verbose_name="Volume global des cr??dits d'heures utilis??s pendant l'ann??e consid??r??e",
        null=True,
        blank=True,
    )
    nombre_reunion_representants_personnel = models.IntegerField(
        verbose_name="Nombre de r??unions avec les repr??sentants du personnel et les d??l??gu??s syndicaux pendant l'ann??e consid??r??e",
        null=True,
        blank=True,
    )
    accords_conclus = models.TextField(
        verbose_name="Dates et signatures et objet des accords conclus dans l'entreprise pendant l'ann??e consid??r??e",
        null=True,
        blank=True,
    )
    nombre_personnes_conge_education_ouvriere = models.IntegerField(
        verbose_name="Nombre de personnes b??n??ficiaires d'un cong?? d'??ducation ouvri??re",
        help_text="Au sens des articles L. 2145-5 et suivants.",
        null=True,
        blank=True,
    )

    #     b) Information et communication
    nombre_heures_reunion_personnel = models.IntegerField(
        verbose_name="Nombre d'heures consacr??es aux diff??rentes formes de r??union du personnel",
        help_text="On entend par r??union du personnel, les r??unions r??guli??res de concertation, concernant les relations et conditions de travail organis??es par l'entreprise.",
        null=True,
        blank=True,
    )
    elements_systeme_accueil = models.TextField(
        verbose_name="El??ments caract??ristiques du syst??me d'accueil",
        null=True,
        blank=True,
    )
    elements_systeme_information = models.TextField(
        verbose_name="El??ments caract??ristiques du syst??me d'information ascendante ou descendante et niveau d'application",
        null=True,
        blank=True,
    )
    elements_systeme_entretiens_individuels = models.TextField(
        verbose_name="El??ments caract??ristiques du syst??me d'entretiens individuels",
        help_text="Pr??ciser leur p??riodicit??.",
        null=True,
        blank=True,
    )
    #     c) Diff??rends concernant l'application du droit du travail
    differends_application_droit_du_travail = models.TextField(
        verbose_name="Diff??rends concernant l'application du droit du travail",
        help_text="Avec indication de la nature du diff??rend et, le cas ??ch??ant, de la solution qui y a mis fin.",
        null=True,
        blank=True,
    )
    #   B-Activit??s sociales et culturelles
    #     a) Activit??s sociales
    contributions_financement_CSE_CSEE = models.TextField(
        verbose_name="Contributions au financement, le cas ??ch??ant, du comit?? social et ??conomique et des comit??s sociaux ??conomiques d'??tablissement",
        null=True,
        blank=True,
    )
    contributions_autres_depenses = CategoryField(
        categories=[
            "logement",
            "transport",
            "restauration",
            "loisirs",
            "vacances",
            "divers",
        ],
        verbose_name="Autres d??penses directement support??es par l'entreprise",
        help_text="D??penses consolid??es de l'entreprise.",
        null=True,
        blank=True,
    )
    #    b) Autres charges sociales
    cout_prestations_maladie_deces = models.IntegerField(
        verbose_name="Co??t pour l'entreprise des prestations compl??mentaires (maladie, d??c??s)",
        help_text="Versements directs ou par l'interm??diaire d'assurances",
        null=True,
        blank=True,
    )
    cout_prestations_vieillesse = models.IntegerField(
        verbose_name="Co??t pour l'entreprise des prestations compl??mentaires (vieillesse)",
        help_text="Versements directs ou par l'interm??diaire d'assurances",
        null=True,
        blank=True,
    )
    equipements_pour_conditions_de_vie = models.TextField(
        verbose_name="Equipements r??alis??s par l'entreprise et touchant aux conditions de vie des salari??s ?? l'occasion de l'ex??cution du travail",
        null=True,
        blank=True,
    )

    # 6?? R??mun??ration des financeurs, en dehors des ??l??ments mentionn??s au 4??
    #   A-R??mun??ration des actionnaires (revenus distribu??s)
    remuneration_actionnaires = models.IntegerField(
        verbose_name="R??mun??ration des actionnaires (revenus distribu??s)",
        null=True,
        blank=True,
    )

    #   B-R??mun??ration de l'actionnariat salari??
    remuneration_actionnariat_salarie = models.IntegerField(
        verbose_name="R??mun??ration de l'actionnariat salari?? (montant des actions d??tenues dans le cadre de l'??pargne salariale, part dans le capital, dividendes re??us)",
        null=True,
        blank=True,
    )

    # 7?? Flux financiers ?? destination de l'entreprise
    #   A-Aides publiques
    aides_financieres = models.TextField(
        verbose_name="Les aides ou avantages financiers consentis ?? l'entreprise par l'Union europ??enne, l'Etat, une collectivit?? territoriale, un de leurs ??tablissements publics ou un organisme priv?? charg?? d'une mission de service public, et leur utilisation",
        help_text="Pour chacune de ces aides, l'employeur indique la nature de l'aide, son objet, son montant, les conditions de versement et d'emploi fix??es, le cas ??ch??ant, par la personne publique qui l'attribue et son utilisation",
        null=True,
        blank=True,
    )

    #   B-R??ductions d'imp??ts
    reductions_impots = models.IntegerField(
        verbose_name="R??ductions d'imp??ts",
        null=True,
        blank=True,
    )

    #   C-Exon??rations et r??ductions de cotisations sociales
    exonerations_cotisations_sociales = models.IntegerField(
        verbose_name="Exon??rations et r??ductions de cotisations sociales",
        null=True,
        blank=True,
    )

    #   D-Cr??dits d'imp??ts
    credits_impots = models.IntegerField(
        verbose_name="Cr??dits d'imp??ts",
        null=True,
        blank=True,
    )

    #   E-M??c??nat
    mecenat = models.IntegerField(
        verbose_name="M??c??nat",
        null=True,
        blank=True,
    )

    #   F-R??sultats financiers
    chiffre_affaires = models.IntegerField(
        verbose_name=" Le chiffre d'affaires",
        null=True,
        blank=True,
    )
    benefices_ou_pertes = models.IntegerField(
        verbose_name="Les b??n??fices ou pertes constat??s",
        null=True,
        blank=True,
    )
    resultats_globaux = CategoryField(
        categories=["valeur", "volume"],
        verbose_name="Les r??sultats globaux de la production",
        null=True,
        blank=True,
    )
    affectation_benefices = models.TextField(
        verbose_name="L'affectation des b??n??fices r??alis??s",
        null=True,
        blank=True,
    )

    # 8?? Partenariats
    #   A-Partenariats conclus pour produire des services ou des produits pour une autre entreprise
    partenariats_pour_produire = models.TextField(
        verbose_name="Partenariats conclus pour produire des services ou des produits pour une autre entreprise",
        null=True,
        blank=True,
    )

    #   B-Partenariats conclus pour b??n??ficier des services ou des produits d'une autre entreprise
    partenariats_pour_beneficier = models.TextField(
        verbose_name="Partenariats conclus pour b??n??ficier des services ou des produits d'une autre entreprise",
        null=True,
        blank=True,
    )

    # 9?? Pour les entreprises appartenant ?? un groupe, transferts commerciaux et financiers entre les entit??s du groupe
    #    A-Transferts de capitaux tels qu'ils figurent dans les comptes individuels des soci??t??s du groupe lorsqu'ils pr??sentent une importance significative
    transferts_de_capitaux = models.TextField(
        verbose_name="Transferts de capitaux tels qu'ils figurent dans les comptes individuels des soci??t??s du groupe lorsqu'ils pr??sentent une importance significative",
        null=True,
        blank=True,
    )

    #    B-Cessions, fusions, et acquisitions r??alis??es
    cessions_fusions_acquisitions = models.TextField(
        verbose_name="Cessions, fusions, et acquisitions r??alis??es",
        null=True,
        blank=True,
    )

    # 10?? Environnement
    #    I-Pour les entreprises soumises ?? la d??claration pr??vue ?? l'article R. 225-105 du code de commerce
    #        A-Politique g??n??rale en mati??re environnementale
    informations_environnementales = models.TextField(
        verbose_name="Informations environnementales pr??sent??es en application du 2?? du A du II de l'article R. 225-105 du code de commerce",
        null=True,
        blank=True,
    )

    #       B-Economie circulaire
    prevention_et_gestion_dechets = models.TextField(
        verbose_name="Pr??vention et gestion de la production de d??chets : ??valuation de la quantit?? de d??chets dangereux d??finis ?? l'article R. 541-8 du code de l'environnement et faisant l'objet d'une ??mission du bordereau mentionn?? ?? l'article R. 541-45 du m??me code",
        null=True,
        blank=True,
    )

    #     C-Changement climatique
    bilan_gaz_effet_de_serre = models.TextField(
        verbose_name="Bilan des ??missions de gaz ?? effet de serre pr??vu par l'article L. 229-25 du code de l'environnement ou bilan simplifi?? pr??vu par l'article 244 de la loi n?? 2020-1721 du 29 d??cembre 2020 de finances pour 2021 pour les entreprises tenues d'??tablir ces diff??rents bilans",
        null=True,
        blank=True,
    )

    #    II-Pour les entreprises non soumises ?? la d??claration pr??vue ?? l'article R. 225-105 du code de commerce
    #        A-Politique g??n??rale en mati??re environnementale
    prise_en_compte_questions_environnementales = models.TextField(
        verbose_name="Organisation de l'entreprise pour prendre en compte les questions environnementales et, le cas ??ch??ant, les d??marches d'??valuation ou de certification en mati??re d'environnement",
        null=True,
        blank=True,
    )

    #       B-Economie circulaire
    #          i-Pr??vention et gestion de la production de d??chets
    quantite_de_dechets_dangereux = models.TextField(
        verbose_name="??valuation de la quantit?? de d??chets dangereux d??finis ?? l'article R. 541-8 du code de l'environnement et faisant l'objet d'une ??mission du bordereau mentionn?? ?? l'article R. 541-45 du m??me code",
        null=True,
        blank=True,
    )
    #          ii-Utilisation durable des ressources
    consommation_eau = models.IntegerField(
        verbose_name="consommation d'eau",
        null=True,
        blank=True,
    )
    consommation_energie = models.IntegerField(
        verbose_name="consommation d'??nergie",
        null=True,
        blank=True,
    )

    #     C-Changement climatique
    #        i-Identification des postes d'??missions directes de gaz ?? effet de serre
    postes_emissions_directes_gaz_effet_de_serre = models.TextField(
        verbose_name="Bilan des ??missions de gaz ?? effet de serre pr??vu par l'article L. 229-25 du code de l'environnement ou bilan simplifi?? pr??vu par l'article 244 de la loi n?? 2020-1721 du 29 d??cembre 2020 de finances pour 2021 pour les entreprises tenues d'??tablir ces diff??rents bilans",
        null=True,
        blank=True,
    )

    def mark_step_as_complete(self, step: int):
        completion_steps = self.completion_steps
        completion_steps[self.STEPS[step]] = True
        self.completion_steps = completion_steps

    def mark_step_as_incomplete(self, step: int):
        completion_steps = self.completion_steps
        completion_steps[self.STEPS[step]] = False
        self.completion_steps = completion_steps

    def step_is_complete(self, step: int):
        return self.completion_steps.get(self.STEPS[step], False)

    @property
    def is_complete(self):
        return all(self.completion_steps.values())


class BDESE_50_300(AbstractBDESE):
    class Meta:
        verbose_name = "BDESE 50 ?? 300 salari??s"
        verbose_name_plural = "BDESE 50 ?? 300 salari??s"

    # D??cret no 2022-678 du 26 avril 2022
    # https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000045680861
    # 1?? Investissements
    # 1?? A - Investissement social
    # 1?? A - a) Evolution des effectifs par type de contrat, par ??ge, par anciennet??
    effectif_mensuel = CategoryField(
        categories=[
            "Janvier",
            "F??vrier",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Aout",
            "Septembre",
            "Octobre",
            "Novembre",
            "D??cembre",
        ],
        help_text="Evolution des effectifs retrac??e mois par mois",
        null=True,
        blank=True,
    )
    effectif_cdi = models.IntegerField(
        verbose_name="Effectif CDI",
        help_text="Nombre de salari??s titulaires d???un contrat de travail ?? dur??e ind??termin??e",
        blank=True,
        null=True,
    )
    effectif_cdd = models.IntegerField(
        verbose_name="Effectif CDD",
        help_text="Nombre de salari??s titulaires d???un contrat de travail ?? dur??e d??termin??e",
        blank=True,
        null=True,
    )
    nombre_salaries_temporaires = models.IntegerField(
        verbose_name="Nombre de salari??s temporaires",
        null=True,
        blank=True,
    )
    nombre_travailleurs_exterieurs = models.IntegerField(
        verbose_name="Nombre de travailleurs ext??rieurs",
        help_text="Nombre de salari??s appartenant ?? une entreprise ext??rieure",
        null=True,
        blank=True,
    )
    nombre_journees_salaries_temporaires = models.IntegerField(
        verbose_name="Nombre de journ??es de travail r??alis??es au cours des douze derniers mois par les salari??s temporaires",
        null=True,
        blank=True,
    )
    nombre_contrats_insertion_formation_jeunes = models.IntegerField(
        verbose_name="Nombre de contrats d'insertion et de formation en alternance ouverts aux jeunes de moins de vingt-six ans",
        null=True,
        blank=True,
    )
    motifs_contrats_cdd_temporaire_temps_partiel_exterieurs = models.TextField(
        verbose_name="Motifs",
        help_text="Motifs ayant conduit l'entreprise ?? recourir aux contrats de travail ?? dur??e d??termin??e, aux contrats de travail temporaire, aux contrats de travail ?? temps partiel, ainsi qu'?? des salari??s appartenant ?? une entreprise ext??rieure",
        null=True,
        blank=True,
    )
    # 1?? A - b) Evolution des emplois par cat??gorie professionnelle
    effectif_homme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        null=True,
        blank=True,
    )
    effectif_femme = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        null=True,
        blank=True,
    )
    actions_prevention_formation = models.TextField(
        verbose_name="Actions de pr??vention et de formation",
        help_text="Indication des actions de pr??vention et de formation que l'employeur envisage de mettre en ??uvre, notamment au b??n??fice des salari??s ??g??s, peu qualifi??s ou pr??sentant des difficult??s sociales particuli??res",
        null=True,
        blank=True,
    )
    # 1?? A - c) Evolution de l'emploi des personnes handicap??es et mesures prises pour le d??velopper
    actions_emploi_personnes_handicapees = models.TextField(
        verbose_name="Actions entreprises ou projet??es",
        help_text="Actions entreprises ou projet??es en mati??re d'embauche, d'adaptation, de r??adaptation ou de formation professionnelle",
        null=True,
        blank=True,
    )
    # D??claration annuelle pr??vue ?? l'article L. 5212-5 ?? l'exclusion des informations mentionn??es ?? l'article D. 5212-4 ;
    # TODO: que contient cette d??claration annuelle pour les 50-300 salari??s et cela se traduit par combien de champs dans notre formulaire ?
    doeth = models.TextField(
        verbose_name="D??claration obligatoire d'emploi des travailleurs handicap??s",
        help_text="D??claration annuelle pr??vue ?? l'article L. 5212-5 ?? l'exclusion des informations mentionn??es ?? l'article D. 5212-4",
        null=True,
        blank=True,
    )
    # 1?? A - d) Evolution du nombre de stagiaires de plus de 16 ans
    nombre_stagiaires = models.IntegerField(
        verbose_name="Nombre de stagiaires de plus de 16 ans",
        null=True,
        blank=True,
    )
    # 1?? A - e) Formation professionnelle : investissements en formation, publics concern??s
    orientations_formation_professionnelle = models.TextField(
        verbose_name="Orientations de la formation professionnelle",
        help_text="Les orientations de la formation professionnelle dans l'entreprise telles qu'elles r??sultent de la consultation pr??vue ?? l'article L. 2312-24",
        null=True,
        blank=True,
    )
    resultat_negociations_L_2241_6 = models.TextField(
        verbose_name="R??sultat ??ventuel des n??gociations pr??vues ?? l'article L. 2241-6",
        null=True,
        blank=True,
    )
    conclusions_verifications_L_6361_1_L_6323_13_L_6362_4 = models.TextField(
        verbose_name="Conclusions ??ventuelles des services de contr??le faisant suite aux v??rifications effectu??es en application des articles L. 6361-1, L. 6323-13 et L. 6362-4",
        null=True,
        blank=True,
    )
    bilan_actions_plan_formation = models.TextField(
        verbose_name="Bilan des actions comprises dans le plan de formation de l'entreprise",
        help_text="Le bilan des actions comprises dans le plan de formation de l'entreprise pour l'ann??e ant??rieure et pour l'ann??e en cours comportant la liste des actions de formation, des bilans de comp??tences et des validations des acquis de l'exp??rience r??alis??s, rapport??s aux effectifs concern??s r??partis par cat??gorie socioprofessionnelle et par sexe",
        null=True,
        blank=True,
    )
    informations_conges_formation = models.TextField(
        verbose_name="Informations relatives aux cong??s de formation",
        help_text="Les informations, pour l'ann??e ant??rieure et l'ann??e en cours, relatives aux cong??s individuels de formation, aux cong??s de bilan de comp??tences, aux cong??s de validation des acquis de l'exp??rience et aux cong??s pour enseignement accord??s ; notamment leur objet, leur dur??e et leur co??t, aux conditions dans lesquelles ces cong??s ont ??t?? accord??s ou report??s ainsi qu'aux r??sultats obtenus",
        null=True,
        blank=True,
    )
    nombre_salaries_beneficaires_abondement = models.IntegerField(
        verbose_name="Nombre des salari??s b??n??ficiaires de l'abondement mentionn?? ?? l'avant-dernier alin??a du II de l'article L. 6315-1",
        null=True,
        blank=True,
    )
    somme_abondement = models.FloatField(
        verbose_name="Sommes vers??es ?? ce titre",
        null=True,
        blank=True,
    )
    nombre_salaries_beneficiaires_entretien_professionnel = models.IntegerField(
        verbose_name="Nombre des salari??s b??n??ficiaires de l'entretien professionnel mentionn?? au I de l'article L. 6315-1.",
        null=True,
        blank=True,
    )
    bilan_contrats_alternance = models.TextField(
        verbose_name="Bilan, pour l'ann??e ant??rieure et l'ann??e en cours, des conditions de mise en ??uvre des contrats d'alternance",
        null=True,
        blank=True,
    )
    emplois_periode_professionnalisation = models.TextField(
        verbose_name="Emplois occup??s pendant et ?? l'issue de leur action ou de leur p??riode de professionnalisation",
        null=True,
        blank=True,
    )
    effectif_periode_professionnalisation_par_age = CategoryField(
        categories=[
            "moins de 30 ans",
            "30 ?? 39 ans",
            "40 ?? 49 ans",
            "50 ans et plus",
        ],
        verbose_name="Effectifs int??ress??s par ??ge",
        null=True,
        blank=True,
    )
    effectif_periode_professionnalisation_par_sexe = CategoryField(
        categories=["homme", "femme"],
        verbose_name="Effectifs int??ress??s par sexe",
        null=True,
        blank=True,
    )
    effectif_periode_professionnalisation_par_niveau_initial = CategoryField(
        categories=[
            "niveau I",
            "niveau II",
            "niveau III",
            "niveau IV",
        ],
        verbose_name="Effectifs int??ress??s par niveau initial de formation",
        null=True,
        blank=True,
    )
    resultats_periode_professionnalisation = models.TextField(
        verbose_name="R??sultats obtenus en fin d'action ou de p??riode de professionnalisation ainsi que les conditions d'appr??ciation et de validation",
        null=True,
        blank=True,
    )
    bilan_cpf = models.TextField(
        verbose_name="Bilan de la mise en ??uvre du compte personnel de formation",
        null=True,
        blank=True,
    )
    # 1?? A - f) Conditions de travail : dur??e du travail dont travail ?? temps partiel et am??nagement du temps de travail ; Donn??es sur le travail ?? temps partiel :
    nombre_salaries_temps_partiel_par_sexe = CategoryField(
        categories=["homme", "femme"],
        verbose_name="Nombre de salari??s travaillant ?? temps partiel",
        null=True,
        blank=True,
    )
    nombre_salaries_temps_partiel_par_qualification = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Qualification des salari??s travaillant ?? temps partiel",
        null=True,
        blank=True,
    )
    horaires_temps_partiel = models.TextField(
        verbose_name="Horaires de travail ?? temps partiel pratiqu??s dans l'entreprise",
        null=True,
        blank=True,
    )
    programme_prevention_risques_pro = models.TextField(
        verbose_name="Programme annuel de pr??vention des risques professionnels et d'am??lioration des conditions de travail",
        help_text="""pr??vu au 2?? de l'article L. 2312-27 ??tabli ?? partir des analyses mentionn??es ?? l'article L. 2312-9 et fixant la liste d??taill??e des mesures devant ??tre prises au cours de l'ann??e ?? venir dans les m??mes domaines afin de satisfaire, notamment :
            i-Aux principes g??n??raux de pr??vention pr??vus aux articles L. 4121-1 ?? L. 4121-5 et L. 4221-1 ;
            ii-A l'information et ?? la formation des travailleurs pr??vues aux articles L. 4141-1 ?? L. 4143-1 ;
            iii-A l'information et ?? la formation des salari??s titulaires d'un contrat de travail ?? dur??e d??termin??e et des salari??s temporaires pr??vues aux articles L. 4154-2 et L. 4154-4 ;
            iv-A la coordination de la pr??vention pr??vue aux articles L. 4522-1 et L. 4522-2 ;
        """,
        null=True,
        blank=True,
    )

    # 1?? B - Investissement mat??riel et immat??riel
    # 1?? B - a) Evolution des actifs nets d'amortissement et de d??pr??ciations ??ventuelles (immobilisations)
    evolution_amortissement = models.TextField(
        verbose_name="Evolution des actifs nets d???amortissement et de d??pr??ciations ??ventuelles (immobilisations)",
        null=True,
        blank=True,
    )
    # 1?? B - b) Le cas ??ch??ant, d??penses de recherche et d??veloppement
    montant_depenses_recherche_developpement = models.IntegerField(
        verbose_name="D??penses de recherche et d??veloppement",
        null=True,
        blank=True,
    )
    # 1?? B - c) Mesures envisag??es en ce qui concerne l'am??lioration, le renouvellement ou la transformation des m??thodes de production et d'exploitation ; et incidences de ces mesures sur les conditions de travail et l'emploi ;
    mesures_methodes_production_exploitation = models.TextField(
        verbose_name="Mesures envisag??es en ce qui concerne l'am??lioration, le renouvellement ou la transformation des m??thodes de production et d'exploitation",
        help_text="et incidences de ces mesures sur les conditions de travail et l'emploi",
        null=True,
        blank=True,
    )

    # 2?? Egalit?? professionnelle entre les femmes et les hommes au sein de l'entreprise
    # 2?? A - Analyse des donn??es chiffr??es
    analyse_egalite_embauche = models.TextField(
        verbose_name="Analyse chiffr??e de la situation en mati??re d'embauche",
        null=True,
        blank=True,
    )
    analyse_egalite_formation = models.TextField(
        verbose_name="Analyse chiffr??e de la situation en mati??re de formation",
        null=True,
        blank=True,
    )
    analyse_egalite_promotion_professionnelle = models.TextField(
        verbose_name="Analyse chiffr??e de la situation en mati??re de promotion professionnelle",
        null=True,
        blank=True,
    )
    analyse_egalite_qualification = models.TextField(
        verbose_name="Analyse chiffr??e de la situation en mati??re de qualification",
        null=True,
        blank=True,
    )
    analyse_egalite_classification = models.TextField(
        verbose_name="Analyse chiffr??e de la situation en mati??re de classification",
        null=True,
        blank=True,
    )
    analyse_egalite_conditions_de_travail = models.TextField(
        verbose_name="Analyse chiffr??e de la situation en mati??re de conditions de travail",
        null=True,
        blank=True,
    )
    analyse_egalite_sante_et_s??curite = models.TextField(
        verbose_name="Analyse chiffr??e de la situation en mati??re de sant?? et de s??curit?? au travail",
        null=True,
        blank=True,
    )
    analyse_egalite_remuneration = models.TextField(
        verbose_name="Analyse chiffr??e de la situation en mati??re de r??mun??ration effective",
        null=True,
        blank=True,
    )
    analyse_egalite_articulation_activite_pro_perso = models.TextField(
        verbose_name="Analyse chiffr??e de la situation en mati??re d'articulation entre l'activit?? professionnelle et l'exercice de la responsabilit?? familiale",
        null=True,
        blank=True,
    )
    analyse_ecarts_salaires = models.TextField(
        verbose_name="Analyse des ??carts de salaires et de d??roulement de carri??re",
        help_text="En fonction de leur ??ge, de leur qualification et de leur anciennet??",
        null=True,
        blank=True,
    )
    evolution_taux_promotion = models.TextField(
        verbose_name="Description de l'??volution des taux de promotion respectifs des femmes et des hommes par m??tiers dans l'entreprise",
        null=True,
        blank=True,
    )

    # 2?? B - Strat??gie d'action
    mesures_prises_egalite = models.TextField(
        verbose_name="Mesures prises au cours de l'ann??e ??coul??e en vue d'assurer l'??galit?? professionnelle",
        help_text="Bilan des actions de l'ann??e ??coul??e et, le cas ??ch??ant, de l'ann??e pr??c??dente. Evaluation du niveau de r??alisation des objectifs sur la base des indicateurs retenus. Explications sur les actions pr??vues non r??alis??es",
        null=True,
        blank=True,
    )
    objectifs_progression = models.TextField(
        verbose_name="Objectifs de progression pour l'ann??e ?? venir et indicateurs associ??s",
        help_text="D??finition qualitative et quantitative des mesures permettant de les atteindre conform??ment ?? l'article R. 2242-2. Evaluation de leur co??t. Ech??ancier des mesures pr??vues",
        null=True,
        blank=True,
    )

    # 3?? Fonds propres, endettement et imp??ts
    capitaux_propres = models.IntegerField(
        verbose_name="Capitaux propres de l'entreprise",
        null=True,
        blank=True,
    )
    emprunts_et_dettes_financieres = models.IntegerField(
        verbose_name="Emprunts et dettes financi??res dont ??ch??ances et charges financi??res",
        null=True,
        blank=True,
    )
    impots_et_taxes = models.IntegerField(
        verbose_name="Imp??ts et taxes",
        null=True,
        blank=True,
    )

    # 4?? R??mun??ration des salari??s et dirigeants, dans l'ensemble de leurs ??l??ments
    # 4?? A - Evolution des r??mun??rations salariales
    # 4?? A - a) Frais de personnel y compris cotisations sociales, ??volutions salariales par cat??gorie et par sexe, salaire de base minimum, salaire moyen ou m??dian, par sexe et par cat??gorie professionnelle
    frais_personnel = models.IntegerField(
        verbose_name="Frais de personnel, y compris cotisations sociales",
        null=True,
        blank=True,
    )
    evolution_salariale_par_categorie = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        null=True,
        blank=True,
    )
    evolution_salariale_par_sexe = CategoryField(
        categories=["homme", "femme"],
        null=True,
        blank=True,
    )
    salaire_base_minimum_par_categorie = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Salaire de base minimum par cat??gorie",
        null=True,
        blank=True,
    )
    salaire_base_minimum_par_sexe = CategoryField(
        verbose_name="Salaire de base minimum par sexe",
        categories=["homme", "femme"],
        null=True,
        blank=True,
    )
    salaire_moyen_par_categorie = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Salaire moyen par cat??gorie",
        null=True,
        blank=True,
    )
    salaire_moyen_par_sexe = CategoryField(
        categories=["homme", "femme"],
        null=True,
        blank=True,
    )
    salaire_median_par_categorie = CategoryField(
        category_type=CategoryType.PROFESSIONNELLE,
        verbose_name="Salaire m??dian par cat??gorie",
        null=True,
        blank=True,
    )
    salaire_median_par_sexe = CategoryField(
        verbose_name="Salaire m??dian par sexe",
        categories=["homme", "femme"],
        null=True,
        blank=True,
    )
    # 4?? A - b) Pour les entreprises soumises aux dispositions de l'article L. 225-115 du code de commerce, montant global des r??mun??rations vis??es au 4?? de cet article
    # https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038610196/
    montant_global_hautes_remunerations = models.IntegerField(
        verbose_name="Montant global des hautes r??mun??rations",
        help_text="Montant global, certifi?? exact par les commissaires aux comptes, s'il en existe, des r??mun??rations vers??es aux personnes les mieux r??mun??r??es, le nombre de ces personnes ??tant de dix ou de cinq selon que l'effectif du personnel exc??de ou non deux cents salari??s ; uniquement pour les entreprises soumises aux dispositions de l'article L. 225-115 du code de commerce",
        null=True,
        blank=True,
    )
    # 4?? A - c) Epargne salariale : int??ressement, participation
    epargne_salariale = models.TextField(
        verbose_name="Epargne salariale : int??ressement, participation",
        null=True,
        blank=True,
    )

    # 5?? Activit??s sociales et culturelles
    montant_contribution_activites_sociales_culturelles = models.IntegerField(
        verbose_name="Montant de la contribution aux activit??s sociales et culturelles",
        help_text="Du comit?? social et ??conomique",
        null=True,
        blank=True,
    )
    mecenat = models.IntegerField(
        verbose_name="M??c??nat",
        null=True,
        blank=True,
    )

    # 6?? R??mun??ration des financeurs, en dehors des ??l??ments mentionn??s au 4??
    # 6?? A - R??mun??ration des actionnaires (revenus distribu??s)
    remuneration_actionnaires = models.IntegerField(
        verbose_name="R??mun??ration des actionnaires (revenus distribu??s)",
        null=True,
        blank=True,
    )

    # 6?? B - R??mun??ration de l'actionnariat salari??
    remuneration_actionnariat_salarie = models.IntegerField(
        verbose_name="R??mun??ration de l'actionnariat salari?? (montant des actions d??tenues dans le cadre de l'??pargne salariale, part dans le capital, dividendes re??us)",
        null=True,
        blank=True,
    )

    # 7?? Flux financiers ?? destination de l'entreprise
    # 7?? A - Aides publiques
    aides_financieres = models.TextField(
        verbose_name="Les aides ou avantages financiers consentis ?? l'entreprise par l'Union europ??enne, l'Etat, une collectivit?? territoriale, un de leurs ??tablissements publics ou un organisme priv?? charg?? d'une mission de service public, et leur utilisation",
        help_text="Pour chacune de ces aides, l'employeur indique la nature de l'aide, son objet, son montant, les conditions de versement et d'emploi fix??es, le cas ??ch??ant, par la personne publique qui l'attribue et son utilisation",
        null=True,
        blank=True,
    )

    # 7?? B - R??ductions d'imp??ts
    reductions_impots = models.IntegerField(
        verbose_name="R??ductions d'imp??ts",
        null=True,
        blank=True,
    )

    # 7?? C - Exon??rations et r??ductions de cotisations sociales
    exonerations_cotisations_sociales = models.IntegerField(
        verbose_name="Exon??rations et r??ductions de cotisations sociales",
        null=True,
        blank=True,
    )

    # 7?? D - Cr??dits d'imp??ts
    credits_impots = models.IntegerField(
        verbose_name="Cr??dits d'imp??ts",
        null=True,
        blank=True,
    )

    # 7?? E - M??c??nat
    mecenat = models.IntegerField(
        verbose_name="M??c??nat",
        null=True,
        blank=True,
    )

    # 7?? F - R??sultats financiers
    chiffre_affaires = models.IntegerField(
        verbose_name=" Le chiffre d'affaires",
        null=True,
        blank=True,
    )
    benefices_ou_pertes = models.IntegerField(
        verbose_name="Les b??n??fices ou pertes constat??s",
        null=True,
        blank=True,
    )
    resultats_globaux = CategoryField(
        categories=["valeur", "volume"],
        verbose_name="Les r??sultats globaux de la production",
        null=True,
        blank=True,
    )
    affectation_benefices = models.TextField(
        verbose_name="L'affectation des b??n??fices r??alis??s",
        null=True,
        blank=True,
    )  # TODO: ?? remplacer par un CategoryField et les affectations possibles???

    # 8?? Partenariats
    # 8?? A - Partenariats conclus pour produire des services ou des produits pour une autre entreprise
    partenariats_pour_produire = models.TextField(
        verbose_name="Partenariats conclus pour produire des services ou des produits pour une autre entreprise",
        null=True,
        blank=True,
    )

    # 8?? B - Partenariats conclus pour b??n??ficier des services ou des produits d'une autre entreprise
    partenariats_pour_beneficier = models.TextField(
        verbose_name="Partenariats conclus pour b??n??ficier des services ou des produits d'une autre entreprise",
        null=True,
        blank=True,
    )
    # 9?? Pour les entreprises appartenant ?? un groupe, transferts commerciaux et financiers entre les entit??s du groupe
    # 9?? A - Transferts de capitaux tels qu'ils figurent dans les comptes individuels des soci??t??s du groupe lorsqu'ils pr??sentent une importance significative
    transferts_de_capitaux = models.TextField(
        verbose_name="Transferts de capitaux tels qu'ils figurent dans les comptes individuels des soci??t??s du groupe lorsqu'ils pr??sentent une importance significative",
        null=True,
        blank=True,
    )

    # 9?? B - Cessions, fusions, et acquisitions r??alis??es
    cessions_fusions_acquisitions = models.TextField(
        verbose_name="Cessions, fusions, et acquisitions r??alis??es",
        null=True,
        blank=True,
    )

    # 10?? Environnement
    # 10?? A - Politique g??n??rale en mati??re environnementale
    prise_en_compte_questions_environnementales = models.TextField(
        verbose_name="Organisation de l'entreprise pour prendre en compte les questions environnementales",
        help_text="et, le cas ??ch??ant, les d??marches d'??valuation ou de certification en mati??re d'environnement",
        null=True,
        blank=True,
    )

    # 10?? B - Economie circulaire
    # 10?? B - a) Pr??vention et gestion de la production de d??chets
    quantite_de_dechets_dangereux = models.TextField(
        verbose_name="??valuation de la quantit?? de d??chets dangereux d??finis ?? l'article R. 541-8 du code de l'environnement et faisant l'objet d'une ??mission du bordereau mentionn?? ?? l'article R. 541-45 du m??me code",
        null=True,
        blank=True,
    )
    # 10?? B - b) Utilisation durable des ressources
    consommation_eau = models.IntegerField(
        verbose_name="consommation d'eau",
        null=True,
        blank=True,
    )
    consommation_energie = models.IntegerField(
        verbose_name="consommation d'??nergie",
        null=True,
        blank=True,
    )

    # 10?? C - Changement climatique
    # 10?? C - a) Identification des postes d'??missions directes de gaz ?? effet de serre produites par les sources fixes et mobiles n??cessaires aux activit??s de l'entreprise (commun??ment appel??es " ??missions du scope 1 ") et, lorsque l'entreprise dispose de cette information, ??valuation du volume de ces ??missions de gaz ?? effet de serre ;
    postes_emissions_directes_gaz_effet_de_serre = models.TextField(
        verbose_name="Identification des postes d'??missions directes de gaz ?? effet de serre",
        help_text="produites par les sources fixes et mobiles n??cessaires aux activit??s de l'entreprise (commun??ment appel??es \"??missions du scope 1\") et, lorsque l'entreprise dispose de cette information, ??valuation du volume de ces ??missions de gaz ?? effet de serre ",
        null=True,
        blank=True,
    )
    # 10?? C - b) Bilan des ??missions de gaz ?? effet de serre pr??vu par l'article L. 229-25 du code de l'environnement ou bilan simplifi?? pr??vu par l'article 244 de la loi n?? 2020-1721 du 29 d??cembre 2020 de finances pour 2021 pour les entreprises tenues d'??tablir ces diff??rents bilans.
    bilan_gaz_effet_de_serre = models.TextField(
        verbose_name="Bilan des ??missions de gaz ?? effet de serre pr??vu par l'article L. 229-25 du code de l'environnement ou bilan simplifi?? pr??vu par l'article 244 de la loi n?? 2020-1721 du 29 d??cembre 2020 de finances pour 2021 pour les entreprises tenues d'??tablir ces diff??rents bilans",
        null=True,
        blank=True,
    )
