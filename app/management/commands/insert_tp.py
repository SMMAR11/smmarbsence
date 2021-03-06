# -*- coding: utf-8 -*-

# Imports
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

class Command(BaseCommand):

	# Définition du message d'aide
	help = 'Automatisation des temps partiels d\'un agent pour l\'année en cours'

	def add_arguments(self, parser):

		# Ajout d'un argument permettant une initialisation complète
		parser.add_argument('--username')
		parser.add_argument('--weekday')
		parser.add_argument('--when')

	def handle(self, *args, **kwargs):

		def all_dates(year, weekday):

			'''
			Sélection de chaque date d'une année pour un jour de la
			semaine
			'''

			# Imports
			from datetime import date
			from datetime import timedelta

			# Récupération du premier temps partiel de l'année
			d = date(year, 1, 1)
			while d.weekday() != weekday:
				d += timedelta(days=1)
			
			# Récupération de tous les temps partiels de l'année
			while d.year == year:
				yield d
				d += timedelta(days=7)

		# Imports
		from app.forms.gest_abs import GererAbsence
		from app.forms.gest_abs import VerifierAbsence
		from app.models import TAbsence
		from app.models import TAnnee
		from app.models import TTypeAbsence
		from app.models import TUtilisateur
		from app.models import TVerificationAbsence
		from datetime import date

		# Nom d'utilisateur
		username = kwargs['username']
		# Jour de la semaine (0 - lundi / 6 - dimanche)
		weekday = kwargs['weekday']
		# Durée
		when = kwargs['when']

		# Si tous les paramètres sont renseignés, alors...
		if (username is not None) \
		and (weekday is not None) \
		and (when is not None) :

			# Année en cours
			year = date.today().year

			# Instances TUtilisateur, TTypeAbsence et TAnnee
			uti = TUtilisateur.objects.filter(username = username).first()
			abs = TTypeAbsence.objects.filter(int_type_abs = 'Temps partiel').first()
			ann = TAnnee.objects.filter(pk = year).first()

			# Si utilisateur, type d'absence et année existants, alors...
			if uti and abs and ann :

				# Pour chaque jour défini de l'année en cours (par
				# exemple tous les mercredis de l'année en cours)...
				for d in all_dates(year=year, weekday=int(weekday)):

					# Définition des paramètres POST
					post = {
						'zl_util': uti.get_pk(),
						'zl_type_abs': abs.get_pk(),
						'zl_annee': year,
						'rb_dt_abs_tranche': 1,
						'zd_dt_abs': d,
						'zl_indisp_dt_abs': when,
						'comm_abs': 'Absence générée automatiquement'
					}

					# Soumission du formulaire
					form = GererAbsence(
						post,
						kw_dt_abs_tranche=1,
						kw_is_automated=True,
						kw_req=None,
						kw_type_abs=abs.get_pk(),
						kw_util=uti
					)

					# Si le formulaire est valide, alors...
					if form.is_valid():

						# Si l'absence n'est pas déjà existante,
						# alors...
						if not TAbsence.objects.filter(
							dt_abs=[d],
							indisp_abs=[when],
							id_type_abs=abs,
							id_util_emett=uti,
							num_annee_id=ann
						).exists():

							# Affichage de la date
							print(d)

							# Création d'une instance TAbsence
							abs_new = form.save()

							# Définition des paramètres POST
							post2 = {
								'est_autor': True,
								'comm_verif_abs': '''
								Absence acceptée automatiquement
								'''
							}

							# Soumission du formulaire de vérification
							form2 = VerifierAbsence(
								post2,
								kw_abs=abs_new
							)

							# Si le formulaire est valide, alors...
							if form2.is_valid():

								# Si la vérification de l'absence n'est
								# pas déjà existante, alors génération
								# automatique d'une instance
								# TVerificationAbsence
								if not TVerificationAbsence.objects \
								.filter(id_abs_mere=abs_new) \
								.exists():
									print(form2.save())