# coding: utf-8

# Import
from django import forms

class GererAbsence(forms.ModelForm) :

	# Import
	from django.conf import settings

	# Initialisation du tableau des indisponibilités pour une date donnée
	TAB_INDISP_ABS = { 'AM' : ('AM', 'Matin'), 'PM' : ('PM', 'Après-midi'), 'WD' : ('WD', 'Journée entière') }

	zl_util = forms.ChoiceField(label = 'Agent concerné')
	zl_type_abs = forms.ChoiceField(choices = [settings.CF_EMPTY_VALUE], label = 'Type de l\'absence')
	zl_annee = forms.ChoiceField(label = 'Année')
	rb_dt_abs_tranche = forms.ChoiceField(
		choices = [(1, 'Oui'), (0, 'Non')],
		initial = 0,
		label = 'L\'absence se porte-t-elle uniquement sur une seule date ?',
		required = False,
		widget = forms.RadioSelect()
	)
	zd_dt_deb_abs = forms.DateField(
		label = 'Date de début de l\'absence <span class="fl-complement">(incluse)</span>',
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date' })
	)
	zl_indisp_dt_deb_abs = forms.ChoiceField(
		choices = [settings.CF_EMPTY_VALUE, TAB_INDISP_ABS['WD'], TAB_INDISP_ABS['PM']],
		label = 'Durée de début de l\'absence'
	)
	zd_dt_fin_abs = forms.DateField(
		label = 'Date de fin de l\'absence <span class="fl-complement">(incluse)</span>',
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date' })
	)
	zl_indisp_dt_fin_abs = forms.ChoiceField(
		choices = [settings.CF_EMPTY_VALUE, TAB_INDISP_ABS['WD'], TAB_INDISP_ABS['AM']],
		label = 'Durée de fin de l\'absence'
	)
	zd_dt_abs = forms.DateField(
		label = 'Date de l\'absence', widget = forms.TextInput(attrs = { 'input-group-addon' : 'date' })
	)
	zl_indisp_dt_abs = forms.ChoiceField(
		choices = [settings.CF_EMPTY_VALUE, TAB_INDISP_ABS['WD'], TAB_INDISP_ABS['AM'], TAB_INDISP_ABS['PM']],
		label = 'Duree de l\'absence'
	)

	class Meta :

		# Import
		from app.models import TAbsence

		fields = ['comm_abs', 'pj_abs']
		model = TAbsence

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import init_mess_err
		from app.models import TAnnee
		from app.models import TGroupeTypeAbsence
		from app.models import TTypeAbsence
		from app.models import TUtilisateur
		from datetime import date
		from dateutil.relativedelta import relativedelta
		from django.conf import settings

		# Initialisation des arguments
		kw_dt_abs_tranche = kwargs.pop('kw_dt_abs_tranche', None)
		self.kw_req = kwargs.pop('kw_req', None)
		kw_type_abs = kwargs.pop('kw_type_abs', None)
		self.kw_util = kwargs.pop('kw_util', None)
		self.kw_is_automated = kwargs.pop('kw_is_automated', False)

		super(GererAbsence, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		if self.kw_util :

			# L'agent est-il secrétaire ?
			if 'S' in self.kw_util.get_type_util__list():
				est_secr = True
			else:
				est_secr = False

			# L'agent est-il super-secrétaire ?
			if est_secr and self.kw_util.get_est_super_secr():
				est_super_secr = True
			else:
				est_super_secr = False

			# Initialisation des choix valides de la liste déroulante des utilisateurs
			if est_secr == True :
				if est_super_secr:
					qs_util = TUtilisateur.objects.all()
				else:
					qs_util = TUtilisateur.objects.filter(en_act=True)
				tab_util = [(u.get_pk(), u.get_nom_complet()) for u in qs_util]
			else :
				if self.kw_util.get_en_act():
					tab_util = [(
						self.kw_util.get_pk(), self.kw_util.get_nom_complet()
					)]
				else:
					tab_util = [settings.CF_EMPTY_VALUE]

			# Définition des utilisateurs valides ainsi que de l'utilisateur par défaut
			self.fields['zl_util'].choices = tab_util
			self.fields['zl_util'].initial = self.kw_util.get_pk()

			# Initialisation des choix valides de la liste déroulante des types d'absence
			tab_type_abs = []
			if est_secr:
				qs_gpe_type_abs = TGroupeTypeAbsence.objects.all()
			else :
				qs_gpe_type_abs = TGroupeTypeAbsence.objects.filter(est_disp=True)
			for gta in qs_gpe_type_abs :
				tab_type_abs.append([
					gta,
					[(ta.get_pk(), ta) for ta in gta.get_type_abs_set().all()]
				])

			# Définition des types d'absence valides
			self.fields['zl_type_abs'].choices += tab_type_abs

			# Initialisation des choix valides de la liste déroulante des années
			if est_super_secr:
				tab_annee = [(a.get_pk(), a) for a in TAnnee.objects.all()]
			else :
				tab_annee = []
				current_date = date.today()
				for a in TAnnee.objects.all() :
					append = False
					# Cas de l'année en cours
					if a.get_plage_conges_annee()[0] <= current_date <= a.get_plage_conges_annee()[1] :
						append = True
					# Cas de l'année suivante (prévision des congés de fin d'année)
					if a.get_plage_conges_annee()[0] <= current_date + relativedelta(months=2) <= a.get_plage_conges_annee()[1] :
						append = True
					if append:
						tab_annee.append((a.get_pk(), a))

				# Réinitialisation des choix valides de la liste déroulante des années en cas de demande d'une absence
				# différente d'un congé pour l'année X-1
				'''
				if kw_type_abs and TTypeAbsence.objects.get(
					pk = kw_type_abs
				).get_gpe_type_abs().get_pk() != settings.DB_PK_DATAS['C_PK'] :
					tab_annee = [(a.get_pk(), a) for a in TAnnee.objects.filter(pk = date.today().year)]
				'''

			# Définition des années valides
			self.fields['zl_annee'].choices = tab_annee

			# Définition de l'année par défaut (année en cours)
			self.fields['zl_annee'].initial = date.today().year

		# Gestion des champs "date"
		if kw_dt_abs_tranche is not None :
			if kw_dt_abs_tranche == 0 :
				del self.fields['zd_dt_abs']
				del self.fields['zl_indisp_dt_abs']
			else :
				del self.fields['zd_dt_deb_abs']
				del self.fields['zl_indisp_dt_deb_abs']
				del self.fields['zd_dt_fin_abs']
				del self.fields['zl_indisp_dt_fin_abs']

	def clean(self) :

		# Imports
		from app.functions import calcul_nbre_j
		from app.functions import init_tranche_dt_abs
		from app.models import TAnnee
		from app.models import TDatesAbsence
		from app.models import TTypeAbsence
		from app.models import TUtilisateur
		from datetime import date
		from django.conf import settings
		from num2words import num2words
		import calendar
		import json

		# Stockage des données du formulaire
		cleaned_data = super(GererAbsence, self).clean()
		val_util = cleaned_data.get('zl_util')
		val_type_abs = cleaned_data.get('zl_type_abs')
		val_annee = cleaned_data.get('zl_annee')
		val_dt_abs_tranche = int(cleaned_data.get('rb_dt_abs_tranche'))
		val_dt_deb_abs = cleaned_data.get('zd_dt_deb_abs')
		val_indisp_dt_deb_abs = cleaned_data.get('zl_indisp_dt_deb_abs')
		val_dt_fin_abs = cleaned_data.get('zd_dt_fin_abs')
		val_indisp_dt_fin_abs = cleaned_data.get('zl_indisp_dt_fin_abs')
		val_dt_abs = cleaned_data.get('zd_dt_abs')
		val_indisp_dt_abs = cleaned_data.get('zl_indisp_dt_abs')

		# Tentative d'obtention d'instances globales
		obj_type_abs = TTypeAbsence.objects.filter(pk = val_type_abs).first()
		obj_gpe_type_abs = obj_type_abs.get_gpe_type_abs() if obj_type_abs else None
		obj_annee = TAnnee.objects.get(pk = val_annee) if val_annee else None
		obj_util = TUtilisateur.objects.get(pk = val_util) if val_util else None

		# L'agent est-il secrétaire ?
		if 'S' in self.kw_util.get_type_util__list():
			est_secr = True
		else:
			est_secr = False

		# L'agent est-il super-secrétaire ?
		if est_secr and self.kw_util.get_est_super_secr():
			est_super_secr = True
		else:
			est_super_secr = False

		if obj_util :

			# Tentative d'obtention de la première instance TStatutsUtilisateur
			obj_statut_util = obj_util.get_statut_util_set().first()

			# Vérification du/des champ(s) "date"
			code_erreur_dt = None
			if obj_statut_util:

				# Stockage de l'année courante
				annee = date.today().year

				if val_dt_abs:
					if (not est_super_secr) and (val_dt_abs < date.today()):
						code_erreur_dt = 'COHERENCE_TEMPORELLE;zd_dt_abs'
					if val_dt_abs < obj_statut_util.get_dt_deb_statut_util():
						code_erreur_dt = 'ARRIVEE_AU_SMMAR;zd_dt_abs'
				if (val_dt_deb_abs) and (val_dt_fin_abs):
					if (not est_super_secr) and (val_dt_deb_abs < date.today()):
						code_erreur_dt = 'COHERENCE_TEMPORELLE;__all__'
					else:
						if val_dt_deb_abs >= val_dt_fin_abs:
							code_erreur_dt = 'ORDRE_DES_DATES;__all__'
						else:
							if val_dt_deb_abs < obj_statut_util.get_dt_deb_statut_util():
								code_erreur_dt = 'ARRIVEE_AU_SMMAR;__all__'

			else:
				code_erreur_dt = 'PAS_DE_STATUT;__all__'

			# Renvoi d'une erreur si un code d'erreur est défini pour le/les champ(s) "date"
			if code_erreur_dt:

				split = code_erreur_dt.split(';')
				if split[0] == 'ARRIVEE_AU_SMMAR':
					self.add_error(
						split[1],
						'''
						L'agent {} est arrivé au SMMAR le {}.
						'''.format(
							obj_util.get_nom_complet(),
							obj_statut_util.get_dt_deb_statut_util__str()
						)
					)
				elif split[0] == 'ORDRE_DES_DATES':
					self.add_error(
						split[1],
						'''
						Veuillez ordonner correctement la date de début de l'absence et la date de fin de l'absence.
						'''
					)
				elif split[0] == 'PAS_DE_STATUT':
					self.add_error(
						split[1],
						'''
						Aucun statut agent n'a été déclaré pour l'agent {}.
						'''.format(obj_util.get_nom_complet())
					)
				elif split[0] == 'COHERENCE_TEMPORELLE' :
					self.add_error(
						split[1],
						'Veuillez respecter une cohérence temporelle.'
					)
			else :

				# Initialisation de la/des date(s) de l'absence
				if (val_dt_abs) and (val_indisp_dt_abs):
					tab = {
						'dt_abs': [val_dt_abs],
						'indisp_abs': [val_indisp_dt_abs]
					}
				elif (val_dt_deb_abs) and (val_dt_fin_abs) and (val_indisp_dt_deb_abs) and (val_indisp_dt_fin_abs):
					tab = {
						'dt_abs': [val_dt_deb_abs, val_dt_fin_abs],
						'indisp_abs': [val_indisp_dt_deb_abs, val_indisp_dt_fin_abs]
					}
				else :
					tab = None

				# Renvoi d'une erreur si aucun jour ouvrable trouvé
				if (tab) and (len([elem['dt_abs'] for elem in init_tranche_dt_abs(tab)]) == 0):
					self.add_error(
						'__all__',
						'L\'absence demandée est constituée uniquement de jours non-ouvrables.'
					)

				if (tab) and (obj_gpe_type_abs) and (obj_annee):

					# Initialisation des bornes selon le groupe de type d'absence
					if obj_gpe_type_abs.get_pk() == settings.DB_PK_DATAS['C_PK'] :
						tab_bornes_dt_abs = [
							obj_annee.get_plage_conges_annee(),
							obj_annee.get_plage_conges_annee__str()
						]
					else :
						tab_bornes_dt_abs = [
							obj_annee.get_plage_rtt_annee(),
							obj_annee.get_plage_rtt_annee__str()
						]

					# Renvoi d'une erreur si l'absence demandée n'est pas incluse dans sa tranche de validité
					erreur = False
					for elem in tab['dt_abs']:
						if not tab_bornes_dt_abs[0][0] <= elem <= tab_bornes_dt_abs[0][1]:
							erreur = True
					if erreur:
						self.add_error(
							'__all__',
							'''
							L'absence doit avoir lieu entre le {0} et le {1}.
							'''.format(*tab_bornes_dt_abs[1])
						)

				if tab :

					# Initialisation des absences déjà autorisées
					tab_abs_autor = []
					for elem in init_tranche_dt_abs(tab) :
						for da in TDatesAbsence.objects.filter(
							id_abs__id_util_emett = obj_util, dt_abs = elem['dt_abs']
						) :
							conflit = False
							if da.get_abs().get_etat_abs() == 1 :
								if da.get_indisp_dt_abs() == 'WD' :
									conflit = True
								elif da.get_indisp_dt_abs() == 'AM' :
									if elem['indisp_dt_abs'] != 'PM' : conflit = True
								elif da.get_indisp_dt_abs() == 'PM' :
									if elem['indisp_dt_abs'] != 'AM' : conflit = True
							if conflit == True : tab_abs_autor.append(da.get_abs().get_pk())

					# Suppression des doublons afin d'avoir le bon nombre d'absences autorisées
					tab_abs_autor = list(set(tab_abs_autor))

					# Définition du message d'erreur (si besoin)
					if len(tab_abs_autor) == 0 :
						message = None
					elif len(tab_abs_autor) == 1 :
						message = '''
						Une absence a déjà été autorisée pour l'agent {}.
						'''.format(obj_util.get_nom_complet())
					else :
						message = '''
						{0} absences ont déjà été autorisées pour l'agent {1}.
						'''.format(num2words(len(tab_abs_autor), lang = 'fr').capitalize(), obj_util.get_nom_complet())

					# Renvoi d'une erreur si une absence est déjà autorisée pendant la période d'absence demandée
					if message : self.add_error('__all__', message)

				if (tab) and (not est_super_secr) and (obj_gpe_type_abs) and (obj_annee):

					# Récupération de la limite de journées paramétrée et
					# valide pour le type d'absence sélectionné
					try:
						lmt_type_abs = json.loads(obj_type_abs.lmt_type_abs)
					except:
						lmt_type_abs = None

					# Si limite de journées, alors...
					if lmt_type_abs:

						# Conversion tableau associatif -> tableau
						tab_dt_abs = [
							[elem['dt_abs'], elem['indisp_dt_abs']
						] for elem in init_tranche_dt_abs(tab)]

						# Pour chaque limite de journées...
						for k1, v1 in lmt_type_abs.items():

							# Si limite au mois, alors...
							if k1 == 'MONTH':

								# Groupement d'objets "date" par mois
								tab_dt_abs__group_by = [[
									j for j in tab_dt_abs if j[0].month == i
								] for i in set(
									map(lambda l: l[0].month, tab_dt_abs)
								)]

								erreur = False
								for elem in tab_dt_abs__group_by:

									# Stockage du mois
									mois = elem[0][0].month

									# Stockage du jeu de données des dates
									# d'absence d'un agent à un mois donné
									# d'une année
									qs_dt_abs = TDatesAbsence.objects.filter(
										dt_abs__month=mois,
										dt_abs__year=obj_annee.get_pk(),
										id_abs__id_util_emett=obj_util
									)

									# Initialisation du nombre de jours
									# autorisés et prévus à un mois donné
									# d'une année
									nbre = 0

									# Cumul du nombre de jours déjà autorisés
									for da in qs_dt_abs:
										obj_verif_abs = da.get_abs().get_verif_abs()
										if obj_verif_abs and obj_verif_abs.get_type_abs_final():
											if obj_verif_abs.get_type_abs_final().get_gpe_type_abs() == obj_gpe_type_abs:
												if da.get_abs().get_etat_abs() == 1:
													if da.get_indisp_dt_abs() == 'WD':
														nbre += 1
													else :
														nbre += 0.5

									# Cumul du nombre de jours prévus
									for elem_2 in elem:
										if elem_2[1] == 'WD':
											nbre += 1
										else :
											nbre += 0.5

									# Vérification du quota
									if nbre > v1 :
										erreur = True

								# Renvoi d'une erreur si le quota n'est
								# pas respecté
								if erreur == True :
									self.add_error(
										'__all__',
										'''
										Quota mensuel non respecté (type
										d'absence : {} / limite : {}).
										'''.format(obj_type_abs, v1)
									)

							# Si limite à la semaine, alors...
							if k1 == 'WEEK':

								# Groupement d'objets "date" par semaine
								tab_dt_abs__group_by = [[
									j for j in tab_dt_abs \
										if j[0].isocalendar()[1] == i
								] for i in set(map(
									lambda l: l[0].isocalendar()[1],
									tab_dt_abs
								))]

								erreur = False
								for elem in tab_dt_abs__group_by:

									# Stockage de la semaine
									week = elem[0][0].isocalendar()[1]

									# Fonction pour récupérer les dates
									# de début et de fin d'une semaine
									# donnée
									def get_date_range_from_week(pyear, pweek):

										# Imports
										import datetime
										import time

										first \
											= datetime.datetime.strptime(
												'{}-W{}-1'.format(
													pyear, pweek
												), 
												'%Y-W%W-%w'
										).date()
										last \
											= first \
											+ datetime.timedelta(days=6.9)

										return first, last 

									# Récupération des dates de début
									# et de fin de la semaine
									firstdate, lastdate \
										= get_date_range_from_week(
											obj_annee.get_pk(), week
									)

									# Stockage du jeu de données des dates
									# d'absence d'un agent à une
									# semaine donnée
									qs_dt_abs = TDatesAbsence.objects.filter(
										dt_abs__gte=firstdate,
										dt_abs__lte=lastdate,
										id_abs__id_util_emett=obj_util
									)

									# Initialisation du nombre de jours
									# autorisés et prévus à une semaine
									# donnée
									nbre = 0

									# Cumul du nombre de jours déjà autorisés
									for da in qs_dt_abs:
										obj_verif_abs = da.get_abs().get_verif_abs()
										if obj_verif_abs and obj_verif_abs.get_type_abs_final():
											if obj_verif_abs.get_type_abs_final().get_gpe_type_abs() == obj_gpe_type_abs:
												if da.get_abs().get_etat_abs() == 1:
													if da.get_indisp_dt_abs() == 'WD':
														nbre += 1
													else :
														nbre += 0.5

									# Cumul du nombre de jours prévus
									for elem_2 in elem:
										if elem_2[1] == 'WD':
											nbre += 1
										else :
											nbre += 0.5

									# Vérification du quota
									if nbre > v1 :
										erreur = True

								# Renvoi d'une erreur si le quota n'est
								# pas respecté
								if erreur == True :
									self.add_error(
										'__all__',
										'''
										Quota hebdomadaire non respecté (type
										d'absence : {} / limite : {}).
										'''.format(obj_type_abs, v1)
									)

							# Stockage des jours de la semaine US
							usweekdays = [
								'MONDAY',
								'TUESDAY',
								'WEDNESDAY',
								'THURSDAY',
								'FRIDAY'
							]
							# Stockage des jours de la semaine FR
							frweekdays = [
								'LUNDI',
								'MARDI',
								'MERCREDI',
								'JEUDI',
								'VENDREDI'
							]
							# Pour chaque jour de la semaine US...
							for i in usweekdays:
								# Si interdiction d'absence, alors...
								if (k1 == 'ALLOW_' + i) and (not v1):
									# Pour chaque date...
									for j in tab_dt_abs:
										# Stockage de l'index US pour
										# comparaison
										usndx = usweekdays.index(i)
										# Si similitude entre jour de
										# la semaine et index US, alors
										# renvoi d'une erreur
										if j[0].weekday() == usndx:
											self.add_error(
												'__all__',
												'''
												Interdiction d'absence
												le {} (type d'absence :
												{}).
												'''.format(
													frweekdays[usndx].lower(),
													obj_type_abs
												)
											)

				if tab and obj_gpe_type_abs :
					if obj_gpe_type_abs.get_pk() == settings.DB_PK_DATAS['CET_PK'] :

						# Détermination du nombre de jours d'absence
						cpt = calcul_nbre_j(tab)

						if cpt > obj_util.get_solde_cet_restant_util() :

							# Détermination de chaque bout composant le message d'erreur
							tab_donn = []
							for elem in [
								(cpt, cpt),
								(obj_util.get_solde_cet_restant_util(), obj_util.get_solde_cet_restant_util__str())
							] :
								bout_phrase = '{} jour'
								if elem[0] > 1 or elem[0] < -1 : bout_phrase += 's'
								tab_donn.append(bout_phrase.format(elem[1]))

							# Renvoi d'une erreur si le nombre de jours posés est supérieur au nombre de jours restant
							# sur le CET de l'agent concerné
							self.add_error(
								'__all__', 
								'''
								Vous souhaitez poser {0}. Or, il vous reste {1} sur le compte épargne temps.
								'''.format(*tab_donn)
							)

	def save(self, commit = True) :

		# Imports
		from app.functions import envoy_mess
		from app.functions import get_tz
		from app.functions import init_tranche_dt_abs
		from app.models import TAnnee
		from app.models import TDatesAbsence
		from app.models import TTypeAbsence
		from app.models import TTypeUtilisateur
		from app.models import TUtilisateur
		from app.models import TVerificationAbsence
		from django.urls import reverse

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_util = cleaned_data.get('zl_util')
		val_type_abs = cleaned_data.get('zl_type_abs')
		val_annee = cleaned_data.get('zl_annee')
		val_dt_deb_abs = cleaned_data.get('zd_dt_deb_abs')
		val_indisp_dt_deb_abs = cleaned_data.get('zl_indisp_dt_deb_abs')
		val_dt_fin_abs = cleaned_data.get('zd_dt_fin_abs')
		val_indisp_dt_fin_abs = cleaned_data.get('zl_indisp_dt_fin_abs')
		val_dt_abs = cleaned_data.get('zd_dt_abs')
		val_indisp_dt_abs = cleaned_data.get('zl_indisp_dt_abs')

		# Obtention d'instances globales
		obj_type_abs = TTypeAbsence.objects.get(pk = val_type_abs)

		# Initialisation de la valeur des attributs dt_abs et indisp_abs
		if (val_dt_abs) and (val_indisp_dt_abs):
			tab = {
				'dt_abs': [val_dt_abs],
				'indisp_abs': [val_indisp_dt_abs]
			}
		else :
			tab = {
				'dt_abs': [val_dt_deb_abs, val_dt_fin_abs],
				'indisp_abs': [val_indisp_dt_deb_abs, val_indisp_dt_fin_abs]
			}

		# L'agent est-il super-secrétaire ?
		est_super_secr = False
		if 'S' in self.kw_util.get_type_util__list():
			if self.kw_util.get_est_super_secr():
				est_super_secr = True

		# Création/modification d'une instance TAbsence
		obj = super(GererAbsence, self).save(commit = False)
		obj.dt_abs = tab['dt_abs']
		obj.dt_emiss_abs = get_tz()
		obj.indisp_abs = tab['indisp_abs']
		obj.src_alerte = obj_type_abs.get_pj_abs_req() if est_super_secr == False else False
		obj.id_type_abs = obj_type_abs
		obj.id_util_connect = self.kw_util
		obj.id_util_emett = TUtilisateur.objects.get(pk = val_util)
		obj.num_annee = TAnnee.objects.get(pk = val_annee)
		obj.save()

		# Lien avec la table t_dates_absence
		obj.get_dt_abs_set().all().delete()
		for elem in init_tranche_dt_abs(tab) :
			TDatesAbsence.objects.create(dt_abs = elem['dt_abs'], indisp_dt_abs = elem['indisp_dt_abs'], id_abs = obj)

		# Si l'absence doit-être vérifiée automatiquement, alors...
		if obj.id_type_abs.id_gpe_type_abs.est_autoverif:

			# Paramètre d'automatisation activé !
			self.kw_is_automated = True

			# Définition des paramètres POST de vérification
			# automatique
			verif_post = {
				'est_autor': True,
				'comm_verif_abs': 'Absence acceptée automatiquement'
			}

			# Soumission du formulaire de vérification automatique
			verif_form = VerifierAbsence(verif_post, kw_abs=obj)

			# Si le formulaire est valide, alors...
			if verif_form.is_valid():
				# Si la vérification de l'absence n'est pas déjà
				# existante, alors génération automatique d'une
				# instance TVerificationAbsence
				if not TVerificationAbsence.objects \
				.filter(id_abs_mere=obj) \
				.exists():
					verif_form.save()

		# Envoi d'un message s'il ne s'agit pas d'une absence générée
		# automatiquement (temps partiels notamment)
		if not self.kw_is_automated:

			if est_super_secr == True :

				# Autorisation automatique de l'absence si super-secrétaire
				TVerificationAbsence.objects.create(
					pk = obj.get_pk(),
					dt_verif_abs = get_tz(),
					est_autor = True,
					id_type_abs_final = obj.get_type_abs(),
					id_util_verif = self.kw_util
				)

				# Définition de l'URL de consultation
				set_reverse = reverse('consult_abs', args = [obj.get_pk()])

				# Initialisation des paramètres du message (envoi unique vers l'agent concerné)
				tab_params_mess = [self.kw_req, {
					'corps_mess' : '''
					L'agent {0} a émis automatiquement une absence du type suivant : « {1} ». Pour consulter les
					modalités de l'absence, veuillez cliquer sur le lien suivant : <a href="{2}">{3}</a>.
					'''.format(
						obj.get_util_connect().get_nom_complet(),
						obj.get_type_abs(),
						set_reverse,
						set_reverse
					),
					'obj_mess' : 'Émission automatique d\'une absence'
				}, [obj.get_util_emett()]]

			else :

				# Obtention du type utilisateur pouvant vérifier l'absence
				get_type_util_verif = obj.get_type_abs().get_gpe_type_abs().get_type_util().get_pk()

				# Définition de l'URL de vérification
				set_reverse = reverse('verif_abs', args = [obj.get_pk()])

				# Initialisation du corps du message
				set_corps_mess = '''
				L'agent {0} souhaite une absence du type suivant : « {1} ». Pour vérifier sa demande d'absence,
				veuillez cliquer sur le lien suivant : <a href="{2}">{3}</a>.
				'''

				# Initialisation des paramètres relatifs au corps du message
				tab_format_corps_mess = [
					obj.get_util_emett().get_nom_complet(),
					obj.get_type_abs(),
					set_reverse,
					set_reverse
				]

				# Réinitialisation du corps du message et de ses paramètres
				if obj.get_util_emett() != obj.get_util_connect() :
					set_corps_mess = '''
					L'agent {0} a demandé une absence du type suivant pour l'agent {1} : « {2} ». Pour vérifier sa
					demande d'absence, veuillez cliquer sur le lien suivant : <a href="{3}">{4}</a>.
					'''
					tab_format_corps_mess.insert(0, obj.get_util_connect().get_nom_complet())

				# Initialisation des paramètres du message (envoi vers les agents concernés)
				tab_params_mess = [self.kw_req, {
					'corps_mess' : set_corps_mess.format(*tab_format_corps_mess),
					'obj_mess' : 'Demande d\'absence'
				}, TTypeUtilisateur.objects.get(pk = get_type_util_verif).get_util_set().all()]

			# Envoi d'un message aux agents concernés
			envoy_mess(*tab_params_mess)

		return obj

class FiltrerAbsences(forms.Form) :

	# Import
	from django.conf import settings
	
	# Champs
	zl_util = forms.ChoiceField(label = 'Agent', required = False)
	zl_annee = forms.ChoiceField(choices = [settings.CF_EMPTY_VALUE], label = 'Année', required = False)

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import get_obj_dt
		from app.functions import init_mess_err
		from app.models import TUtilisateur
		from datetime import date
		from django.conf import settings

		# Initialisation des arguments
		kw_util = kwargs.pop('kw_util', None)

		super(FiltrerAbsences, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		if kw_util :

			# Initialisation des choix valides de la liste déroulante des utilisateurs
			if 'S' in kw_util.get_type_util__list() :
				tab_util = [(u.get_pk(), u.get_nom_complet()) for u in TUtilisateur.objects.all()]
				tab_util.insert(0, settings.CF_EMPTY_VALUE)
			else :
				tab_util = [(kw_util.get_pk(), kw_util.get_nom_complet())]

			# Définition des utilisateurs valides et l'utilisateur par défaut
			self.fields['zl_util'].choices = tab_util
			self.fields['zl_util'].initial = kw_util.get_pk()

		self.fields['zl_annee'].choices += [(elem, elem) for elem in get_obj_dt('YEARS')]
		self.fields['zl_annee'].initial = date.today().year

	def init_dtab(self, _req, *args, **kwargs) :

		# Imports
		from app.models import TAbsence
		from django.urls import reverse

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_annee = self.fields['zl_annee'].initial
			val_util = self.fields['zl_util'].initial
		else :
			val_annee = _req.POST.get('zl_annee')
			val_util = _req.POST.get('zl_util')

		# Définition des conditions de la requête
		tab_filter = {}
		if val_annee : tab_filter['num_annee'] = val_annee
		if val_util : tab_filter['id_util_emett'] = val_util

		# Initialisation des données de la datatable
		tab = [[
			a.get_util_emett().get_nom_complet(),
			a.get_type_abs_final(),
			a.get_dt_abs__fr_str(),
			a.get_annee(),
			a.get_etat_abs(True),
			'<a href="{}" class="inform-icon pull-right" title="Consulter l\'absence"></a>'.format(
				reverse('consult_abs', args = [a.get_pk()])
			)
		] for a in TAbsence.objects.filter(**tab_filter)]

		return '''
		<div class="custom-table" id="dtab_chois_abs">
			<table border="1" bordercolor="#DDD">
				<thead>
					<tr>
						<th>Nom complet de l'agent</th>
						<th>Type de l'absence</th>
						<th>Date de l'absence</th>
						<th>Année de l'absence</th>
						<th>État de l'absence</th>
						<th></th>
					</tr>
				</thead>
				<tbody>{}</tbody>
			</table>
		</div>
		'''.format(''.join(['<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tr])) for tr in tab]))

class FiltrerVerificationAbsences(forms.Form) :

	# Import
	from django.conf import settings
	
	# Champ
	zl_util = forms.ChoiceField(choices = [settings.CF_EMPTY_VALUE], label = 'Agent', required = False)

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import init_mess_err
		from app.models import TUtilisateur

		# Initialisation des arguments
		self.kw_util = kwargs.pop('kw_util', None)

		super(FiltrerVerificationAbsences, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		# Initialisation des choix valides de la liste déroulante des utilisateurs
		tab_util = [(u.get_pk(), u.get_nom_complet()) for u in TUtilisateur.objects.all()]

		# Définition des utilisateurs valides et l'utilisateur par défaut
		self.fields['zl_util'].choices += tab_util

	def init_dtab(self, _req, *args, **kwargs) :

		# Imports
		from app.models import TUtilisateur
		from django.urls import reverse

		# Stockage des données du formulaire
		val_util = self.fields['zl_util'].initial if _req.method == 'GET' else _req.POST.get('zl_util')

		# Définition des conditions de la requête
		tab_filter = {}
		if val_util : tab_filter['id_util_emett'] = val_util

		# Initialisation des données de la datatable
		tab = [[
			a.get_util_emett().get_nom_complet(),
			a.get_type_abs(),
			a.get_dt_abs__fr_str(),
			'<a href="{}" class="pull-right verify-icon" title="Vérifier l\'absence"></a>'.format(
				reverse('verif_abs', args = [a.get_pk()])
			)
		] for a in TUtilisateur.objects.get(pk = self.kw_util).get_abs_a_verif__list(tab_filter)]

		return '''
		<div class="custom-table" id="dtab_chois_verif_abs">
			<table border="1" bordercolor="#DDD">
				<thead>
					<tr>
						<th>Nom complet de l'agent</th>
						<th>Type de l'absence</th>
						<th>Date de l'absence</th>
						<th></th>
					</tr>
				</thead>
				<tbody>{}</tbody>
			</table>
		</div>
		'''.format(''.join(['<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tr])) for tr in tab]))

class VerifierAbsence(forms.ModelForm) :

	class Meta :

		# Import
		from app.models import TVerificationAbsence

		fields = ['comm_verif_abs', 'est_autor']
		model = TVerificationAbsence
		widgets = { 'est_autor' : forms.RadioSelect(choices = [(True, 'Oui'), (False, 'Non')]) }

	def __init__(self, *args, **kwargs) :

		# Import
		from app.functions import init_mess_err

		# Initialisation des arguments
		self.kw_abs = kwargs.pop('kw_abs', None)
		self.kw_req = kwargs.pop('kw_req', None)
		self.kw_util_connect = kwargs.pop('kw_util_connect', None)

		super(VerifierAbsence, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

	def clean(self) :

		# Imports
		from app.models import TDatesAbsence
		from django.conf import settings
		from num2words import num2words

		# Stockage des données du formulaire
		cleaned_data = super(VerifierAbsence, self).clean()
		val_est_autor = cleaned_data.get('est_autor')

		if val_est_autor == True :

			# Renvoi d'une erreur si l'agent n'est plus en activité
			if self.kw_abs.get_util_emett().get_en_act() == False :
				self.add_error(
					'__all__',
					'L\'agent {} n\'est plus en activité.'.format(self.kw_abs.get_util_emett().get_nom_complet())
				)

			# Initialisation des absences déjà autorisées
			tab_abs_autor = []
			for daa in self.kw_abs.get_dt_abs_set().all() :
				for da in TDatesAbsence.objects.filter(
					dt_abs = daa.get_dt_abs(), id_abs__id_util_emett = self.kw_abs.get_util_emett()
				) :
					conflit = False
					if da.get_abs().get_etat_abs() == 1 :
						if da.get_indisp_dt_abs() == 'WD' :
							conflit = True
						elif da.get_indisp_dt_abs() == 'AM' :
							if daa.get_indisp_dt_abs() != 'PM' : conflit = True
						elif da.get_indisp_dt_abs() == 'PM' :
							if daa.get_indisp_dt_abs() != 'AM' : conflit = True
					if conflit == True : tab_abs_autor.append(da.get_abs().get_pk())

			# Suppression des doublons afin d'avoir le bon nombre d'absences autorisées
			tab_abs_autor = list(set(tab_abs_autor))

			# Définition du message d'erreur (si besoin)
			if len(tab_abs_autor) == 0 :
				message = None
			elif len(tab_abs_autor) == 1 :
				message = '''
				Une absence a déjà été autorisée pendant cette absence pour l'agent {}.
				'''.format(self.kw_abs.get_util_emett().get_nom_complet())
			else :
				message = '''
				{0} absences ont déjà été autorisées pendant cette absence pour l'agent {1}.
				'''.format(
					num2words(len(tab_abs_autor), lang = 'fr').capitalize(),
					self.kw_abs.get_util_emett().get_nom_complet()
				)

			# Renvoi d'une erreur en cas d'un quelconque conflit entre plusieurs absences
			if message : self.add_error('__all__', message)

			# Renvoi d'une erreur si le solde restant prévisionnel sur un CET est négatif
			if self.kw_abs.get_type_abs().get_gpe_type_abs().get_pk() == settings.DB_PK_DATAS['CET_PK'] :
				if self.kw_abs.get_util_emett().get_solde_cet_restant_util(
					self.kw_abs.get_util_emett().get_solde_cet_util() - self.kw_abs.get_nbre_dt_abs()
				) < 0 :
					self.add_error(
						'__all__',
						'Vous ne pouvez pas avoir un solde restant négatif sur votre compte épargne temps.'
					)

	def save(self, commit = True) :

		# Imports
		from app.functions import envoy_mess
		from app.functions import get_tz
		from django.urls import reverse

		# Création/modification d'une instance TVerificationAbsence
		obj = super(VerifierAbsence, self).save(commit = False)
		obj.pk = self.kw_abs.get_pk()
		obj.dt_verif_abs = get_tz()
		obj.id_type_abs_final = self.kw_abs.get_type_abs()
		obj.id_util_verif = self.kw_util_connect
		obj.save()

		# Envoi d'un message s'il ne s'agit pas d'une absence vérifiée
		# automatiquement (temps partiels notamment)
		if obj.get_util_verif():

			# Définition de l'URL de vérification
			set_reverse = reverse('consult_abs', args = [obj.get_pk()])

			# Initialisation des paramètres du message (envoi unique vers l'agent concerné)
			tab_params_mess = [self.kw_req, {
				'corps_mess' : '''
				L'agent {0} a {1} votre demande d'absence. Pour en savoir plus, veuillez cliquer sur le lien suivant :
				<a href="{2}">{3}</a>.
				'''.format(
					obj.get_util_verif().get_nom_complet(),
					'autorisé' if obj.get_est_autor() == True else 'refusé',
					set_reverse,
					set_reverse
				),
				'obj_mess' : '{} d\'absence'.format('Autorisation' if obj.get_est_autor() == True else 'Refus')
			}, [obj.get_abs().get_util_emett()]]

			# Envoi d'un message à l'agent concerné
			envoy_mess(*tab_params_mess)

		return obj

class ModifierTypeAbsenceFinal(forms.ModelForm) :

	# Import
	from django.conf import settings

	# Champ
	zl_type_abs_final = forms.ChoiceField(choices = [settings.CF_EMPTY_VALUE], label = 'Type final de l\'absence')

	class Meta :

		# Import
		from app.models import TVerificationAbsence

		fields = []
		model = TVerificationAbsence

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import init_mess_err
		from app.models import TGroupeTypeAbsence

		super(ModifierTypeAbsenceFinal, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		# Initialisation des choix valides de la liste déroulante des types d'absence
		tab_type_abs = []
		for gta in TGroupeTypeAbsence.objects.all() :
			tab_type_abs.append([gta, [(ta.get_pk(), ta) for ta in gta.get_type_abs_set().all()]])

		# Définition des types d'absence valides
		self.fields['zl_type_abs_final'].choices += tab_type_abs
		if self.instance.get_pk() :
			self.fields['zl_type_abs_final'].initial = self.instance.get_type_abs_final().get_pk()

	def save(self, commit = True) :

		# Import
		from app.models import TTypeAbsence

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_type_abs_final = cleaned_data.get('zl_type_abs_final')

		# Modification d'une instance TVerificationAbsence
		obj = super(ModifierTypeAbsenceFinal, self).save(commit = False)
		obj.id_type_abs_final = TTypeAbsence.objects.get(pk = val_type_abs_final)
		obj.save()

		return obj

class InsererPieceJustificativeAbsence(forms.ModelForm) :

	# Import
	from app.validators import valid_pdf

	# Champ
	zu_pj_abs = forms.FileField(
		label = 'Insérer le justificatif d\'absence <span class="fl-complement">(fichier PDF)</span>',
		validators = [valid_pdf]
	)

	class Meta :

		# Import
		from app.models import TAbsence

		fields = []
		model = TAbsence

	def __init__(self, *args, **kwargs) :

		# Import
		from app.functions import init_mess_err

		super(InsererPieceJustificativeAbsence, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		self.fields['zu_pj_abs'].initial = self.instance.get_pj_abs() if self.instance.get_pk() else None

	def save(self, commit = True) :

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_pj_abs = cleaned_data.get('zu_pj_abs')

		# Écrasement du fichier PDF sur le serveur (si besoin)
		if self.instance.get_pk() and val_pj_abs != self.instance.get_pj_abs() : self.instance.get_pj_abs().delete()

		# Modification d'une instance TAbsence
		obj = super(InsererPieceJustificativeAbsence, self).save(commit = False)
		obj.pj_abs = val_pj_abs
		obj.save()

		return obj