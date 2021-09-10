# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu à vignettes relatif au module "Calendrier des absences"
_req : Objet "requête"
'''
@verif_acces('cal_abs')
def get_menu(_req) :

	# Imports
	from app.functions import get_menu
	from app.functions import init_menu_vign
	from app.functions import init_vign
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Mise en forme du menu à vignettes du module de gestion des absences
		menu = init_menu_vign([init_vign(
			elem, ['item_href', 'item_img', 'item_name']
		) for elem in get_menu(_req)['cal_abs']['mod_items'].values()], 2)

		# Affichage du template
		output = render(_req, './cal_abs/get_menu.html', { 'menu' : menu, 'title' : 'Calendrier des absences' })

	return output

'''
Affichage du calendrier des absences prévisionnelles ou traitement d'une requête quelconque
_req : Objet "requête"
'''
@verif_acces('cal_abs', 'cal_abs_prev')
def cal_abs_prev(_req):
	return cal_abs(_req=_req, _status='prev')

'''
Affichage du calendrier des absences validées ou traitement d'une requête quelconque
_req : Objet "requête"
'''
@verif_acces('cal_abs')
def cal_abs_val(_req):
	return cal_abs(_req=_req, _status='val')

'''
Affichage du calendrier des absences ou traitement d'une requête quelconque
_req : Objet "requête"
_status : Statut de l'absence
'''
def cal_abs(_req, _status) :

	# Imports
	from app.forms.cal_abs import FiltrerCalendrierAbsences
	from app.functions import get_obj_dt
	from app.functions import init_fm
	from app.functions import init_form
	from app.models import TDatesAbsence
	from app.models import TGroupeUtilisateur
	from app.models import TUtilisateur
	from datetime import date
	from datetime import datetime
	from django.http import HttpResponse
	from django.shortcuts import render
	from django.template.context_processors import csrf
	import calendar
	import dateutil.relativedelta
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_filtr_cal_abs = 'FiltrerCalendrierAbsences'

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	'''
	Initialisation d'un calendrier
	_mois : Mois
	_annee : Année
	_util : Utilisateurs
	Retourne une chaîne de caractères
	'''
	def init_cal_mois(_mois, _annee, _util, _obj) :

		# Imports
		from app.functions import est_ouvr
		from app.models import TAnnee
		from datetime import date
		import dateutil.relativedelta

		# Initialisation des jours de la semaine au format français (abréviations)
		tab_j_sem = get_obj_dt('WEEKDAYS', True)

		# Obtention de l'indice du premier jour du mois ainsi que le nombre de jours composant celui-ci
		tab_mr = calendar.monthrange(_annee, _mois)
		ind_prem_j_mois = tab_mr[0]
		nbre_j_mois = tab_mr[1]

		# Initialisation du jeu de données des utilisateurs concernés par le calendrier
		if isinstance(_util, str) == True :
			if _util == '__all__' : qs_util = TUtilisateur.objects.filter(en_act = True)
		else :
			qs_util = TUtilisateur.objects.filter(
				en_act = True, pk__in = _util
			) if len(_util) > 0 else TUtilisateur.objects.none()

		# Début d'initialisation de la balise <thead/>
		compt = ind_prem_j_mois
		tab_elem_lg2 = ['']
		for i in range(nbre_j_mois) :
			tab_elem_lg2.append('{0} {1}'.format(tab_j_sem[compt % 7], i + 1))
			compt += 1
		tab_thead_lg2 = ['<th>{}</th>'.format(elem) for elem in tab_elem_lg2]

		# Initialisation des numéros de semaine du mois
		tab_elem_lg1 = [date(_annee, _mois, i + 1).isocalendar()[1] for i in range(nbre_j_mois)]
		tab_num_sem_mois = [[j for j in tab_elem_lg1 if j == i] for i in set(map(lambda l : l, tab_elem_lg1))]
		tab_num_sem_mois = { i[0] : i for i in tab_num_sem_mois }

		# Fin d'initialisation de la balise <thead/>
		tab_thead_lg1 = ['<th></th>']
		cpt_j_mois = 1
		while cpt_j_mois <= nbre_j_mois :

			# Récupération du numéro de semaine du jour lié avec le compteur
			num_sem_j_mois = date(_annee, _mois, cpt_j_mois).isocalendar()[1]

			tab_thead_lg1.append(
				'<th colspan="{0}">{1}</th>'.format(len(tab_num_sem_mois[num_sem_j_mois]), num_sem_j_mois)
			)

			# Mise à jour du compteur
			cpt_j_mois += len(tab_num_sem_mois[num_sem_j_mois])

		# Détermination du profil de visualisation du calendrier des absences (si non-secrétaire, alors l'agent ne peut
		# savoir le type d'absence)
		coul = True if 'S' in obj_util.get_type_util__list() else False

		# Initialisation des lignes de la balise <tbody/>
		tab_tbody = []
		for a in qs_util :

			tab_elem = [[a.get_nom_complet(), '']]
			for i in range(nbre_j_mois) :

				# Stockage de la date du jour
				dt_jour = date(_annee, _mois, i + 1)

				# Initialisation du contenu de la balise <td/>
				cont_td = ''

				# Initialisation des types d'indisponibilités pour une journée
				indisponibilities = []

				for dta in TDatesAbsence.objects.filter(dt_abs = dt_jour, id_abs__id_util_emett = a) :

					# Définition des statuts de validation d'absence à prendre ne compte sur le calendrier
					valid_statuses = [1] if _status == 'val' else [0, 1]

					if dta.get_abs().get_etat_abs() in valid_statuses :
					
						# Définition des styles CSS pour chaque cas d'absence (matin, après-midi ou journée entière)
						tab_css_div = {
							'AM' : 'display: inline-block; float: left; width: 50%;',
							'PM' : 'display: inline-block; float: right; width: 50%;',
							'WD' : 'width: 100%;'
						}

						# Détermination des styles CSS et de l'intitulé complet du groupe de type d'absence
						donn_cal_abs = dta.get_donn_cal_abs()
						set_style = tab_css_div[dta.indisp_dt_abs]
						set_title = ''
						if (coul == True) or (a == obj_util) or (donn_cal_abs['abrev_gpe_type_abs'] == 'TLT'):
							set_style += ' background-color: {};'.format(donn_cal_abs['coul_gpe_type_abs'])
							set_title = ' title="{}"'.format(donn_cal_abs['int_dt_abs'])

						# Mise en forme de la balise <td/>
						if dta.indisp_dt_abs not in indisponibilities :
							cont_td += '<div class="mc-absence" style="{0}"{1}></div>'.format(set_style, set_title)
							# Empilement des types d'indisponibilités afin de ne pas perturber le CSS du calendrier en
							# cas de doublon d'absences en attente de validation
							indisponibilities.append(dta.indisp_dt_abs)

				tab_elem.append([cont_td, '' if est_ouvr(dt_jour) == True else 'background-color: #E9F2DC;'])
			tab_tbody.append('<tr>{}</tr>'.format(''.join(
				['<td style="{0}">{1}</td>'.format(elem[1], elem[0]) for elem in tab_elem]
			)))

		# Initialisation des bornes d'affichage des boutons "Mois précédent" et "Mois suivant"
		tab_bornes_dt = [
			date(TAnnee.objects.last().get_pk(), 1, 1),
			date(TAnnee.objects.first().get_pk() + 1, 5, 31)
		]

		# Obtention d'un objet "date" relatif au premier jour du mois courant
		obj_dt = date(_annee, _mois, 1)

		return '''
		
		<div class="custom-well">
			<span class="clone-title">Calendrier des absences {0} - {1}</span>
		</div>
		<div style="text-align: right;">
			<span class="filter-icon icon-with-text" data-target="#fm_filtr_cal_abs" data-toggle="modal">
				Filtrer le calendrier des absences par
			</span>
		</div>
		<span class="clone-body">
			<div class="month-calendar">
				<table border="1" bordercolor="#DDD">
					<colgroup>
						<col style="width: 160px;">
					</colgroup>
					<thead>
						<tr>{2}</tr>
						<tr>{3}</tr>
					</thead>
					<tbody>{4}</tbody>
				</table>
			</div>
		</span>
		<span action="?action=initialiser-calendrier&mois=precedent" class="icon-with-text previous-icon" 
		onclick="trait_get(event, null);" style="{5}">Mois précédent</span>
		<div style="float: right; display: inline;">
			<span action="?action=initialiser-calendrier&mois=suivant" class="icon-with-text next-icon"
			onclick="trait_get(event, null);" style="{6}">Mois suivant</span>
		</div>
		'''.format(
			'validées' if _status == 'val' else 'prévisionnelles',
			'{0} {1}'.format(get_obj_dt('MONTHS')[_mois - 1], _annee),
			''.join(tab_thead_lg1),
			''.join(tab_thead_lg2),
			''.join(tab_tbody),
			'display: none;' if obj_dt - dateutil.relativedelta.relativedelta(months = 1) < tab_bornes_dt[0] else '',
			'display: none;' if obj_dt + dateutil.relativedelta.relativedelta(months = 1) > tab_bornes_dt[1] else '',
		)

	if _req.method == 'GET' :

		# Initialisation du calendrier (mois précédent ou suivant)
		if 'action' in _req.GET and _req.GET['action'] == 'initialiser-calendrier' :
			if 'mois' in _req.GET :

				# Conversion vers le type "date"
				obj_dt = datetime.strptime(_req.session['mois_cal'], '%Y-%m-%d')

				# Calcul de la date avec un intervalle de +/- 1 mois
				if _req.GET['mois'] == 'precedent' :
					dt = obj_dt - dateutil.relativedelta.relativedelta(months = 1)
				if _req.GET['mois'] == 'suivant' :
					dt = obj_dt + dateutil.relativedelta.relativedelta(months = 1)

				# Affichage du contenu
				output = HttpResponse(
					json.dumps({ 'success' : {
						'content' : init_cal_mois(dt.month, dt.year, _req.session['tab_util_cal'], obj_util),
						'selector' : '#za_cal_abs'
					}}),
					content_type = 'application/json'
				)

				# Rafraîchissement des variables de session
				_req.session['mois_cal'] = str(dt.strftime('%Y-%m-%d'))

		else :

			# Initialisation de chaque formulaire
			form_filtr_cal_abs = init_form(FiltrerCalendrierAbsences(prefix = pref_filtr_cal_abs))

			# Initialisation des variables de session
			_req.session['mois_cal'] = str(date.today())
			_req.session['tab_util_cal'] = '__all__'

			# Initialisation des fenêtres modales
			tab_fm = [
				init_fm('agrand_cal_abs', ''),
				init_fm(
					'filtr_cal_abs',
					'Filtrer le calendrier des absences par', 
					'''
					<form action="" method="post" name="form_filtr_cal_abs" onsubmit="trait_post(event);">
						<input name="csrfmiddlewaretoken" type="hidden" value="{0}">
						<div class="row">
							<div class="col-sm-6">{1}</div>
							<div class="col-sm-6">{2}</div>
						</div>
						{3}
						{4}
						<button class="center-block custom-btn green-btn" type="submit">Valider</button>
					</form>
					'''.format(
						csrf(_req)['csrf_token'],
						form_filtr_cal_abs['zl_mois'],
						form_filtr_cal_abs['zl_annee'],
						form_filtr_cal_abs['zcc_gpe_util'],
						form_filtr_cal_abs['zcc_util']
					)
				)
			]

			# Affichage du template
			output = render(_req, './cal_abs/main.html', {
				'cal' : init_cal_mois(date.today().month, date.today().year, '__all__', obj_util),
				'tab_fm' : tab_fm,
				'title' : 'Calendrier des absences ' + ('validées' if _status == 'val' else 'prévisionnelles'),
			})

	else :

		# Soumission du formulaire
		form_filtr_cal_abs = FiltrerCalendrierAbsences(_req.POST, prefix = pref_filtr_cal_abs)

		if form_filtr_cal_abs.is_valid() :

			# Stockage des données du formulaire
			cleaned_data = form_filtr_cal_abs.cleaned_data
			val_mois = cleaned_data.get('zl_mois')
			val_annee = cleaned_data.get('zl_annee')
			val_gpe_util = cleaned_data.get('zcc_gpe_util')
			val_util = cleaned_data.get('zcc_util')

			# Initialisation des utilisateurs concernés par le calendrier
			tab_util = [TUtilisateur.objects.get(pk = u).get_pk() for u in val_util]
			for gu in val_gpe_util :
				for u in TGroupeUtilisateur.objects.get(pk = gu).get_util_set().all() : tab_util.append(u.get_pk())

			# Affichage du contenu
			output = HttpResponse(
				json.dumps({ 'success' : {
					'mf_content' : init_cal_mois(int(val_mois), int(val_annee), tab_util, obj_util),
					'selector' : '#za_cal_abs'
				}}),
				content_type = 'application/json'
			)

			# Rafraîchissement des variables de session
			_req.session['mois_cal'] = str(date(int(val_annee), int(val_mois), 1))
			_req.session['tab_util_cal'] = tab_util

		else :

			# Affichage des erreurs
			tab_errs = { '{0}-{1}'.format(
				pref_filtr_cal_abs, cle
			) : val for cle, val in form_filtr_cal_abs.errors.items() }
			output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

	return output