# coding: utf-8

# Import
from django import forms

class FiltrerCalendrierAbsences(forms.Form) :

	# Imports
	from app.functions import get_obj_dt
	from datetime import date
	from django.conf import settings

	# Initialisation des mois au format français
	tab_mois = [(index + 1, elem) for index, elem in enumerate(get_obj_dt('MONTHS'))]
	tab_mois.insert(0, settings.CF_EMPTY_VALUE)
	
	# Champs
	zl_mois = forms.ChoiceField(choices = tab_mois, initial = date.today().month, label = 'Mois')
	zl_annee = forms.ChoiceField(choices = [settings.CF_EMPTY_VALUE], initial = date.today().year, label = 'Année')
	zcc_gpe_util = forms.MultipleChoiceField(
		label = 'Groupes d\'utilisateur|Intitulé|__zcc__', required = False, widget = forms.SelectMultiple()
	)
	zcc_util = forms.MultipleChoiceField(
		label = 'Utilisateurs|Nom complet|__zcc__', required = False, widget = forms.SelectMultiple()
	)

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import get_obj_dt
		from app.functions import init_mess_err
		from app.models import TGroupeUtilisateur
		from app.models import TUtilisateur
		from datetime import date

		super(FiltrerCalendrierAbsences, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		# Initialisation des choix valides des listes déroulantes
		tab_annee = [(elem, elem) for elem in [date.today().year + 1, *get_obj_dt('YEARS')]]
		tab_gpe_util = [[
			gu.get_pk(), '|'.join([gu.get_str_complet(), '__zcc__'])
		] for gu in TGroupeUtilisateur.objects.all()]
		tab_util = [[
			u.get_pk(), '|'.join([u.get_nom_complet(), '__zcc__'])
		] for u in TUtilisateur.objects.filter(en_act = True)]

		# Définition des choix valides
		self.fields['zl_annee'].choices += tab_annee
		self.fields['zcc_gpe_util'].choices = tab_gpe_util
		self.fields['zcc_util'].choices = tab_util

	def clean(self) :

		# Imports
		from app.models import TGroupeUtilisateur
		from datetime import date

		# Stockage des données du formulaire
		cleaned_data = super(FiltrerCalendrierAbsences, self).clean()
		val_mois = cleaned_data.get('zl_mois')
		val_annee = cleaned_data.get('zl_annee')
		val_gpe_util = cleaned_data.get('zcc_gpe_util')
		val_util = cleaned_data.get('zcc_util')

		# Renvoi d'une erreur si aucun utilisateur choisi
		erreur = False
		if val_gpe_util :
			nbre_util = 0
			for gu in val_gpe_util :
				nbre_util += TGroupeUtilisateur.objects.get(pk = gu).get_util_set().filter(en_act = True).count()
			if nbre_util == 0 : erreur = True
		else :
			if not val_util : erreur = True
		if erreur == True : self.add_error('__all__', 'Aucun agent en activité n\'a été trouvé par la requête.')

		# Renvoi d'une erreur si aucun calendrier des absences n'est disponible
		if val_mois and val_annee and int(val_mois) > 5 and int(val_annee) == date.today().year + 1 :
			self.add_error('__all__', 'Aucun calendrier n\'est disponible pour cette période.')