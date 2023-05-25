from django import forms
from django.core.exceptions import ValidationError

from entreprises.forms import SirenField
from entreprises.models import DENOMINATION_MAX_LENGTH
from entreprises.models import Entreprise
from utils.forms import DsfrForm


class SirenForm(DsfrForm):
    siren = SirenField()


class EligibiliteForm(DsfrForm, forms.ModelForm):
    denomination = forms.CharField()

    class Meta:
        model = Entreprise
        fields = ["effectif", "bdese_accord", "denomination", "siren"]

    forme_juridique = forms.ChoiceField(
        choices=(
            ('EI', 'Entreprise individuelle (EI)'),
            ('EURL', 'Entreprise unipersonnelle à responsabilité limitée (EURL)'),
            ('SA', 'Société anonyme (SA)'),
            ('SARL', 'Société à responsabilité limitée (SARL)'),
            ('SAS', 'Société par actions simplifiée (SAS)'),
            ('SASU', 'Société par actions simplifiée unipersonnelle (SASU)'),
            ('SCA', 'Société en commandite par actions (SCA)'),
            ('Scop', 'Société coopérative de production (Scop)'),
            ('SCS', 'Société en commandite simple (SCS)'),
            ('SE', 'Société européenne (SE)'),
            ('SNC', 'Société en nom collectif (SNC)'),
            ('autre', 'Autre'),
        )
    )
    cotee = forms.BooleanField(label="Société côtée")
    bilan = forms.IntegerField(label="Total de bilan")
    ca_net = forms.IntegerField(
        label="Chiffre d'affaires net",
    )
    nombre_moyen_de_salaries_employes_au_cours_d_exercice = forms.IntegerField(
        label="Nombre moyen de salariés (employés au cours de l'exercice)"
    )
    nombre_moyen_de_salaries_permanents = forms.IntegerField(
        label="Nombre moyen de salariés permanents"
    )
    appartient_a_un_groupe_de_societes_dont_la_societe_mere_a_son_siege_social_en_France_et_effectif_500_salaries = (
        forms.BooleanField()
    )
    nombre_salaries_fr = forms.IntegerField(
        label="Nombre de salariés (société + filiales françaises directes et indirectes dont le siège social est fixé sur le territoire français)"
    )
    nombre_salaries_monde = forms.IntegerField(
        label="Nombre de salariés (société + toutes filiales directes et indirectes)"
    )
    plan_de_vigilance_societe_mere = forms.BooleanField(
        label="La société mère a mis en place un plan de vigilance relatif à l'activité de la société et de l'ensemble des filiales ou sociétés qu'elle contrôle"
    )
    systeme_management_energie = forms.BooleanField(
        label="L'entreprise a mis en place d'un système de management de l'énergie"
    )

    def clean_denomination(self):
        denomination = self.cleaned_data.get("denomination")
        return denomination[:DENOMINATION_MAX_LENGTH]


class NaiveCaptchaField(forms.CharField):
    def validate(self, value):
        super().validate(value)
        try:
            int(value)
            raise ValidationError("La réponse doit être écrite en toutes lettres")
        except ValueError:
            pass
        if value.lower() != "trois":
            raise ValidationError("La somme est incorrecte")


class ContactForm(DsfrForm):
    email = forms.EmailField(label="Votre adresse e-mail")
    subject = forms.CharField(
        label="Sujet",
        max_length=255,
    )
    message = forms.CharField(widget=forms.Textarea())
    sum = NaiveCaptchaField(
        label="Pour vérifier que vous n'êtes pas un robot, merci de répondre en toutes lettres à la question 1 + 2 = ?",
        max_length=10,
    )
