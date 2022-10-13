# coding: utf-8

# Import
from django.conf import settings

def get_alert(_req) :

	# Imports
	from app.functions import get_tz
	from app.models import TAbsence
	from app.models import TUtilisateur
	from datetime import date
	from django.conf import settings
	from django.urls import reverse
	from num2words import num2words

	tab_alert = []

	# Initialisation des niveaux de priorités
	tab_prior = {
		'F' : 'background-color: #FDEE00;',
		'M' : 'background-color: #F8B862;',
		'E' : 'background-color: #FF0921;'
	}

	# Tentative d'obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk) if _req.user.is_authenticated else None

	if obj_util :
		if 'S' in obj_util.get_type_util__list() :
			for u in TUtilisateur.objects.all() :

				# Gestion des alertes liées aux statuts agent
				if u.get_statut_util_set().count() > 0 :

					# Vérification de l'activité d'un statut agent
					statut = False
					for su in u.get_statut_util_set().all() :
						if date.today() > su.get_dt_deb_statut_util() : statut = True

					# Renvoi d'une alerte si aucun statut agent en activité
					if statut == False :
						tab_alert.append({
							'code_alert' : 'SA',
							'descr_alert' : '''
							Aucun statut agent n'est actif pour l'agent {0} jusqu'au {1}.
							'''.format(
								u.get_nom_complet(), u.get_statut_util_set().first().get_dt_deb_statut_util__str()
							),
							'lien_alert' : reverse('consult_agent', args = [u.get_pk()]),
							'nat_alert' : 'Statut de l\'agent',
							'prior_alert' : [1, tab_prior['F']],
							'util_alert' : u
						})

					# Calcul du nombre d'absences sans statut actif
					nbre_abs_sans_statut = 0
					for a in u.get_abs_set().all() :
						if a.get_etat_abs() > -1 and \
						a.get_dt_abs()[0] < u.get_statut_util_set().first().get_dt_deb_statut_util() :
							nbre_abs_sans_statut += 1

					if nbre_abs_sans_statut > 0 :

						# Définition du début du message d'alerte
						if nbre_abs_sans_statut > 1 :
							bout_mess = '''
							{} absences ont déjà été autorisées, ou sont en attente de vérification
							'''.format(num2words(nbre_abs_sans_statut, lang = 'fr').capitalize())
						else :
							bout_mess = 'Une absence a déjà été autorisée, ou est en attente de vérification'

						# Renvoi d'une alerte si une absence est autorisée ou en attente avant l'arrivée d'un agent au
						# SMMAR
						tab_alert.append({
							'code_alert' : 'SA',
							'descr_alert' : '''
							{0} pour l'agent {1} avant le {2} (date d'arrivée de l'agent au SMMAR).
							'''.format(
								bout_mess,
								u.get_nom_complet(),
								u.get_statut_util_set().first().get_dt_deb_statut_util__str()
							),
							'lien_alert' : reverse('consult_agent', args = [u.get_pk()]),
							'nat_alert' : 'Statut de l\'agent',
							'prior_alert' : [3, tab_prior['E']],
							'util_alert' : u
						})

				else :

					# Renvoi d'une alerte si aucun statut agent déclaré
					tab_alert.append({
						'code_alert' : 'SA',
						'descr_alert' : '''
						Aucun statut agent n'a été déclaré pour l'agent {}.
						'''.format(u.get_nom_complet()),
						'lien_alert' : reverse('consult_agent', args = [u.get_pk()]),
						'nat_alert' : 'Statut de l\'agent',
						'prior_alert' : [3, tab_prior['E']],
						'util_alert' : u
					})

				for du in u.get_decompt_util_set().reverse() :
					tab_mess = []

					# Définition du message d'erreur
					mess = '''
					Le nombre de jours de __GTA__ transférés sur le compte épargne temps de l'agent {0} pour l'année
					{1} est supérieur au nombre de jours restants.
					'''.format(u.get_nom_complet(), du.get_annee())

					# Empilement du tableau des erreurs
					if u.get_nbre_j_non_transf(True, du.get_annee().get_pk()) < 0 :
						tab_mess.append(mess.replace('__GTA__', 'congés payés'))
					if u.get_nbre_j_non_transf(False, du.get_annee().get_pk()) < 0 :
						tab_mess.append(mess.replace('__GTA__', 'RTT'))

					# Renvoi d'une alerte si incohérence des transactions entrantes (dûe à un changement de statut)
					for elem in tab_mess :
						tab_alert.append({
							'code_alert' : 'CET',
							'descr_alert' : elem,
							'lien_alert' : reverse('consult_agent', args = [u.get_pk()]),
							'nat_alert' : 'Compte épargne temps',
							'prior_alert' : [3, tab_prior['E']],
							'util_alert' : u
						})

				# Calcul du nombre de transactions sur le CET sans statut actif
				nbre_trans_cet_util_sans_statut = 0
				for tcu in u.get_trans_cet_util_set().all() :
					if u.get_decompt_util_set().filter(num_annee = tcu.get_annee().get_pk()).count() == 0 :
						nbre_trans_cet_util_sans_statut += 1
				for a in u.get_abs_set().all() :
					if a.get_etat_abs() > -1 and \
					a.get_type_abs().get_gpe_type_abs().get_pk() == settings.DB_PK_DATAS['CET_PK'] and \
					a.get_dt_abs()[0] < u.get_statut_util_set().first().get_dt_deb_statut_util() :
						nbre_trans_cet_util_sans_statut += 1

				if nbre_trans_cet_util_sans_statut > 0 :

					# Définition du début du message d'alerte
					if nbre_trans_cet_util_sans_statut > 1 :
						bout_mess = '''
						{0} transactions sur le compte épargne temps de l'agent {1} ont déjà été effectuées
						'''.format(
							num2words(nbre_trans_cet_util_sans_statut, lang = 'fr').capitalize(),
							u.get_nom_complet()
						)
					else :
						bout_mess = '''
						Une transaction sur le compte épargne temps de l'agent {} a déjà été effectuée
						'''.format(u.get_nom_complet())

					# Renvoi d'une alerte si une transaction sur le CET a été effectuée avant l'arrivée d'un agent au
					# SMMAR
					tab_alert.append({
						'code_alert' : 'CET',
						'descr_alert' : '''
						{0} avant le {1} (date d'arrivée de l'agent au SMMAR).
						'''.format(bout_mess, u.get_statut_util_set().first().get_dt_deb_statut_util__str()),
						'lien_alert' : reverse('consult_agent', args = [u.get_pk()]),
						'nat_alert' : 'Compte épargne temps',
						'prior_alert' : [3, tab_prior['E']],
						'util_alert' : u
					})

				# Renvoi d'une alerte en cas d'incohérence à propos du solde restant sur un CET
				if u.get_solde_cet_restant_util() > 60 :
					mess = '''
					Le solde restant du compte épargne temps de l'agent {0} est supérieur à 60 jours ({1} jours
					actuellement).
					'''
				elif u.get_solde_cet_restant_util() < 0 :
					mess = '''
					Le solde restant du compte épargne temps de l'agent {0} est inférieur à 0 jour ({1} jour(s)
					actuellement).
					'''
				else :
					mess = None
				if mess :
					tab_alert.append({
						'code_alert' : 'CET',
						'descr_alert' : mess.format(u.get_nom_complet(), u.get_solde_cet_restant_util__str()),
						'lien_alert' : reverse('consult_agent', args = [u.get_pk()]),
						'nat_alert' : 'Compte épargne temps',
						'prior_alert' : [3, tab_prior['E']],
						'util_alert' : u
					})

		for a in TAbsence.objects.filter(src_alerte = True) :
			if 'S' in obj_util.get_type_util__list() or a.get_util_emett() == obj_util :

				# Définition du nombre de jours restants pour insérer un justificatif d'absence
				nbre_j_inser_pj_abs = 7 - (get_tz().date() - a.get_dt_emiss_abs().date()).days

				# Définition du niveau de priorité de l'alerte (s'il y a)
				if nbre_j_inser_pj_abs < 3 :
					prior_alert = [1, tab_prior['E']]
				elif nbre_j_inser_pj_abs < 5 :
					prior_alert = [2, tab_prior['M']]
				elif nbre_j_inser_pj_abs < 8 :
					prior_alert = [1, tab_prior['F']]

				if a.get_etat_abs() == 0 :
					tab_alert.append({
						'code_alert' : 'PJ_ABS',
						'descr_alert' : '''
						{0}, il vous reste {1} jour(s) pour insérer le justificatif d'absence relatif à votre absence
						du type suivant : « {2} » (alerte également envoyée aux secrétaires).
						'''.format(a.get_util_emett().get_nom_complet(), nbre_j_inser_pj_abs, a.get_type_abs()),
						'lien_alert' : reverse('consult_abs', args = [a.get_pk()]),
						'nat_alert' : 'Insertion d\'un justificatif d\'absence',
						'prior_alert' : prior_alert,
						'util_alert' : None
					})

	return {
		'alerts_list' : sorted(tab_alert, key = lambda l : (-l['prior_alert'][0], l['nat_alert'])),
		'badge_color' : 'background-color: #FF0921;' if len(tab_alert) > 0 else 'background-color: #82C46C;'
	}

'''
Obtention de données dans un template
_req : Objet "requête"
Retourne un tableau associatif
'''
def get_donn(_req) :

	# Imports
	from app.apps import AppConfig
	from app.models import TUtilisateur

	# Tentative d'obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk) if _req.user.is_authenticated else None

	# Comptage du nombre de messages non-lus provenant de la boîte de réception
	if obj_util :
		nbre_mess_util_bdr_non_lus = obj_util.get_mess_util_set_bdr_non_lus__count()
		if nbre_mess_util_bdr_non_lus == 0 :
			mess_util__count = None
		else :
			mess_util__count = ' ({})'.format(nbre_mess_util_bdr_non_lus)
	else :
		mess_util__count = None

	return {
		'app_name' : AppConfig.verbose_name,
		'db_pk_datas' : [(cle, val) for cle, val in settings.DB_PK_DATAS.items()],
		'mess_util__count' : mess_util__count or '',
		'u' : obj_util
	}

'''
Obtention des derniers messages non-archivés
_req : Objet "requête"
Retourne un tableau associatif
'''
def get_mess(_req) :

	# Imports
	from app.models import TUtilisateur
	from django.urls import reverse
	from django.template.defaultfilters import safe

	ddown = None

	if _req.user.is_authenticated :

		# Obtention d'une instance TUtilisateur
		obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

		# Stockage des derniers messages non-archivés
		qs_mess_util = obj_util.get_qs_mess_util_set(False, 5)
		
		if qs_mess_util.count() > 0 :

			# Mise en forme du gabarit d'un message
			gab_mess = '''
			<li class="navbar-message">
				<a href="{0}">
					<div>
						<span class="nm-sender">
							{1}
							<span class="{2}"></span>
						</span>
						<span class="nm-date">Le {3}</span>
					</div>
					<span class="nm-subject">{4}</span>
					<span class="nm-body">{5}</span> 
				</a>
			</li>
			'''

			# Initialisation du menu déroulant des derniers messages non-archivés
			tab_elem_ddown = [gab_mess.format(
				reverse('consult_mess', args = [mu.get_pk()]),
				mu.get_mess().get_emett_mess(),
				'fa fa-check-circle-o' if mu.get_est_lu() == True else 'fa fa-circle-o',
				mu.get_mess().get_dt_mess__str(),
				mu.get_mess().get_obj_mess(),
				mu.get_mess().get_corps_mess__text()
			) for mu in qs_mess_util]

			# Intégration de l'option "Afficher tous les messages"
			tab_elem_ddown.append(
				'<li><a href="{}" class="text-center">Afficher tous les messages</a></li>'.format(reverse('get_mess'))
			)

			# Mise en forme du menu déroulant (au moins un message)
			ddown = '''
			<li class="dropdown">
				<a class="dropdown-toggle" data-toggle="dropdown" href="#">
					<span class="fa fa-lg fa-envelope-o"></span>
					<span class="caret"></span>
				</a>
				<ul class="dropdown-menu dm-messages">{}</ul>
			</li>
			'''.format(''.join(tab_elem_ddown))

		else :

			# Mise en forme du menu déroulant (aucun message)
			ddown = '''
			<li><a href="{}" class="fa fa-lg fa-envelope-o" title="Aucun message"></a></li>
			'''.format(reverse('get_mess'))

	return { 'last_messages' : safe(ddown or '') }

'''
Obtention des fenêtres modales permanentes
_req : Objet "requête"
Retourne un tableau associatif
'''
def init_fm_perm(_req) :

	# Imports
	from app.apps import AppConfig
	from app.functions import init_fm
	from app.models import TUtilisateur
	from django.template.defaultfilters import safe

	# Initialisation des fenêtres modales
	if _req.user.is_authenticated :

		# Obtention d'une instance TUtilisateur
		obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

		tab_fm = [
			init_fm(
				'ger_mode_super_secr',
				'{} le mode super-secrétaire'.format(
					'Activer' if obj_util.get_est_super_secr() == False else 'Désactiver'
				)
			),
			init_fm('logout', 'Déconnexion de la plateforme {}'.format(AppConfig.verbose_name))
		]
	else :
		tab_fm = []

	return { 'modals' : safe(''.join(tab_fm)) }

'''
Initialise les différents menus de l'application
_req : Objet "requête"
Retourne un tableau associatif
'''
def init_menus(_req) :

	# Imports
	from app.functions import get_menu
	from django.template.defaultfilters import safe

	output = {}

	# Initialisation du menu utilisateur
	menu = get_menu(_req)

	# Initialisation des éléments "panel" du menu latéral
	tab_panels = []
	for cle, val in menu.items() :
		if len(val['mod_items']) > 0 :

			# Mise en forme d'un élément "panel" contenant des sous-éléments
			panel = '''
			<div class="panel">
				<div class="panel-heading">
					<span class="panel-title">
						<a href="#pnl_{mod_key}" data-parent="#side-menu" data-toggle="collapse">
							<img src="{mod_img}">
							{mod_name}
						</a>
					</span>
				</div>
				<div class="collapse panel-collapse" id="pnl_{mod_key}">
					<div class="panel-body">
						<table>{mod_items}</table>
					</div>
				</div>
			</div>
			'''.format(
				mod_img = val['mod_img'],
				mod_items = ''.join(['<tr><td><a href="{0}">{1}</a></td></tr>'.format(
					elem['item_href'], elem['item_name']
				) for elem in val['mod_items'].values()]),
				mod_key = cle,
				mod_name = val['mod_name']
			)

		else :

			# Mise en forme d'un élément "panel" contenant aucun sous-élément
			panel = '''
			<div class="panel">
				<div class="panel-heading">
					<span class="panel-title">
						<a href="{mod_href}">
							<img src="{mod_img}">
							{mod_name}
						</a>
					</span>
				</div>
			</div>
			'''.format(
				mod_href = val['mod_href'],
				mod_img = val['mod_img'],
				mod_name = val['mod_name']
			)
			
		tab_panels.append(panel)

	# Mise en forme du menu latéral et empilage du tableau associatif de sortie
	menu_lat = '<div class="panel-group" id="side-menu">{}</div>'.format(''.join(tab_panels))
	output['side_menu'] = safe(menu_lat)

	# Initialisation des éléments du navigateur
	tab_elem_nav = []
	for cle, val in menu.items() :
		if len(val['mod_items']) > 0 :
			li = '''
			<li class="dropdown">
				<a class="dropdown-toggle" data-toggle="dropdown" href="#">
					{0}
					<span class="caret"></span>
				</a>
				<ul class="dropdown-menu">{1}</ul>
			</li>
			'''.format(
				val['mod_name'],
				''.join(['<li><a href="{0}">{1}</a></li>'.format(
					elem['item_href'], elem['item_name']
				) for elem in val['mod_items'].values()]))
		else :
			li = '<li><a href="{0}">{1}</a></li>'.format(val['mod_href'], val['mod_name'])
		tab_elem_nav.append(li)

	# Mise en forme du navigateur et empilage du tableau associatif de sortie
	nav = '<ul class="nav navbar-nav">{}</ul>'.format(''.join(tab_elem_nav))
	output['top_menu'] = safe(nav)

	return output

'''
Application de tâches précises dans le temps
_req : Objet "requête"
Retourne un tableau associatif vierge
'''
def set_tasks(_req) :

	# Imports
	from app.models import TAnnee
	from app.models import TUtilisateur
	from datetime import date

	# Stockage de l'année actuelle
	annee = date.today().year

	if TAnnee.objects.filter(pk = annee).count() == 0 :
		TAnnee.create(annee)
		for u in TUtilisateur.objects.all() : u.calc_proratas()

	return {}