# -*- coding: utf-8 -*-

# Imports
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

class Command(BaseCommand) :

	# Import
	from app.apps import AppConfig

	# Définition du message d'aide
	help = 'Initialisation de la base de données {}'.format(AppConfig.verbose_name)

	def handle(self, *args, **kwargs) :

		# Imports
		from app.apps import AppConfig
		from app.models import TAnnee
		from app.models import TGroupeTypeAbsence
		from app.models import TRolesUtilisateur
		from app.models import TTypeAbsence
		from app.models import TTypeUtilisateur
		from app.models import TUtilisateur
		from datetime import date
		from decouple import config
		from django.conf import settings

		# Initialisation des types d'utilisateur
		tab_type_util = [['A', 'Agent'], ['D', 'Direction'], ['S', 'Secrétaire']]
		for elem in tab_type_util :
			if TTypeUtilisateur.objects.filter(pk = elem[0]).count() == 0 :
				TTypeUtilisateur.objects.create(pk = elem[0], int_type_util = elem[1])

		# Création du compte agent principal
		set_username = config('MAIN_ACCOUNT_USERNAME')
		if TUtilisateur.objects.filter(username = set_username).count() == 0 :

			# Création d'une instance TUtilisateur
			obj_util = TUtilisateur(
				email = config('MAIN_ACCOUNT_EMAIL'),
				first_name = config('MAIN_ACCOUNT_FIRSTNAME'),
				is_staff = True,
				is_superuser = True,
				last_name = config('MAIN_ACCOUNT_LASTNAME'),
				username = set_username
			)
			obj_util.set_password('password')
			obj_util.save()

			# Lien avec la table t_roles_utilisateur
			for elem in tab_type_util :
				TRolesUtilisateur.objects.create(
					code_type_util = TTypeUtilisateur.objects.get(pk = elem[0]), id_util = obj_util
				)

		# Initialisation des années
		for i in range(settings.SMMAR_YEAR_CREATION, date.today().year + 1) :
			if TAnnee.objects.filter(pk = i).count() == 0 : TAnnee.create(i)

		# Initialisation des groupes de type d'absence ainsi que des types d'absence
		tab_gpe_type_abs = [{
			'abrev_gpe_type_abs' : 'C',
			'est_disp' : True,
			'int_gpe_type_abs' : 'Congés',
			'ordre_zl_gpe_type_abs' : 1,
			'code_type_util' : TTypeUtilisateur.objects.get(pk = 'D')
		}, {
			'abrev_gpe_type_abs' : 'RTT',
			'est_disp' : True,
			'int_gpe_type_abs' : 'RTT',
			'ordre_zl_gpe_type_abs' : 1,
			'code_type_util' : TTypeUtilisateur.objects.get(pk = 'S')
		}, {
			'abrev_gpe_type_abs' : 'CET',
			'est_disp' : True,
			'int_gpe_type_abs' : 'Compte épargne temps',
			'ordre_zl_gpe_type_abs' : 1,
			'code_type_util' : TTypeUtilisateur.objects.get(pk = 'S')
		}]
		for elem in tab_gpe_type_abs :
			if TGroupeTypeAbsence.objects.filter(int_gpe_type_abs = elem['int_gpe_type_abs']).count() == 0 :
				obj_gpe_type_abs = TGroupeTypeAbsence.objects.create(**elem)
				TTypeAbsence.objects.create(
					int_type_abs = elem['int_gpe_type_abs'], pj_abs_req = False, id_gpe_type_abs = obj_gpe_type_abs
				)

		print('La base de données {} a été initialisée avec succès.'.format(AppConfig.verbose_name))