# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu à vignettes relatif au module de réalisation d'états
_req : Objet "requête"
'''
@verif_acces('real_etats')
def get_menu(_req) :

	# Imports
	from app.functions import get_menu
	from app.functions import init_menu_vign
	from app.functions import init_vign
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Mise en forme du menu à vignettes du module de réalisation d'états
		menu = init_menu_vign([init_vign(
			elem, ['item_href', 'item_img', 'item_name']
		) for elem in get_menu(_req)['real_etats']['mod_items'].values()], 3)

		# Affichage du template
		output = render(_req, './real_etats/get_menu.html', { 'menu' : menu, 'title' : 'Réalisation d\'états' })

	return output

'''
Affichage du formulaire de réalisation d'un état ou traitement d'une requête quelconque
_req : Objet "requête"
_gby : Regroupement ou sélection d'absences ?
'''
@verif_acces('real_etats')
def filtr_abs(_req, _gby) :

	# Imports
	from app.forms.real_etats import FiltrerAbsences
	from app.functions import gener_cdc
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import prep_dtab
	from app.functions import transform_bool
	from app.models import TAbsence
	from app.models import TUtilisateur
	from django.http import HttpResponse
	from django.shortcuts import render
	from django.template.context_processors import csrf
	import csv
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_filtr_abs = 'FiltrerAbsences'

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	if _req.method == 'GET' :
		if 'action' in _req.GET :
			if _req.GET['action'] == 'exporter-csv' and 'group-by' in _req.GET \
			and _req.GET['group-by'] in ['off', 'on'] :

				# Génération d'un fichier au format CSV
				output = HttpResponse(content_type = 'text/csv', charset = 'cp1252')
				output['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(gener_cdc())

				# Accès en écriture
				writer = csv.writer(output, delimiter = ';')

				# Initialisation des données
				tab_lg = _req.session['filtr_abs'] if 'filtr_abs' in _req.session else []

				# Définition de l'en-tête
				if _gby == False :
					header = [
						'Agent ayant émis l\'absence',
						'Date d\'émission de l\'absence',
						'Agent concerné',
						'Type de l\'absence',
						'Année',
						'Date de l\'absence',
						'Justificatif d\'absence',
						'Commentaire (phase de pré-validation)',
						'Agent ayant vérifié l\'absence',
						'Date de vérification de l\'absence',
						'L\'absence est-elle autorisée ?',
						'Type final de l\'absence',
						'Commentaire (phase de post-validation)'
					]
				else :
					header = [
						'Nom complet de l\'agent/des agents',
						'Type de l\'absence',
						'Année de l\'absence',
						'État de l\'absence',
						'Nombre d\'absences',
						'Nombre de jours d\'absence'
					]

				# Ajout de l'en-tête
				writer.writerow(header)

				for elem in tab_lg :

					# Définition des données de la nouvelle ligne
					if _gby == False :

						# Obtention d'une instance TAbsence
						obj_abs = TAbsence.objects.get(pk = elem[0])

						# Ajout des données "pré-validation"
						body = [
							obj_abs.get_util_connect().get_nom_complet() if obj_abs.get_util_connect() else None,
							obj_abs.get_dt_emiss_abs__str(),
							obj_abs.get_util_emett().get_nom_complet(),
							obj_abs.get_type_abs(),
							obj_abs.get_annee(),
							obj_abs.get_dt_abs__fr_str(),
							_req.build_absolute_uri(str(obj_abs.get_pj_abs())) if obj_abs.get_pj_abs() else None,
							obj_abs.get_comm_abs()
						]

						# Ajout des données "post-validation" si définies
						if obj_abs.get_verif_abs() :
							body += [
								obj_abs.get_verif_abs().get_util_verif().get_nom_complet() \
								if obj_abs.get_verif_abs().get_util_verif() else None,
								obj_abs.get_verif_abs().get_dt_verif_abs__str(),
								transform_bool(obj_abs.get_verif_abs().get_est_autor()),
								obj_abs.get_verif_abs().get_type_abs_final(),
								obj_abs.get_verif_abs().get_comm_verif_abs()
							]

					else :
						body = elem

					# Ajout d'une nouvelle ligne
					writer.writerow(body)

		else :

			# Initialisation du formulaire et de ses attributs
			form_filtr_abs = FiltrerAbsences(prefix = pref_filtr_abs, kw_gby = _gby, kw_util = obj_util)
			_form_filtr_abs = init_form(form_filtr_abs)

			# Définition de l'attribut <title/>
			if _gby == False :
				title = 'Réalisation d\'états en sélectionnant des absences'
			else :
				title = 'Réalisation d\'états en regroupant des absences'

			# Initialisation des fenêtres modales
			tab_fm = [init_fm(
				'filtr_abs',
				'Filtrer les absences par',
				'''
				<form action="" method="post" name="form_select_abs" onsubmit="trait_post(event);">
					<input name="csrfmiddlewaretoken" type="hidden" value="{0}">
					{1}
					<div class="row">
						<div class="col-sm-6">{2}</div>
						<div class="col-sm-6">{3}</div>
					</div>
					<span class="theme-color">Période de début d'absence</span>
					<div class="row">
						<div class="col-sm-6">{4}</div>
						<div class="col-sm-6">{5}</div>
					</div>
					{6}
					{7}
					{8}
					<button class="center-block custom-btn green-btn" type="submit">Valider</button>
				</form>
				'''.format(
					csrf(_req)['csrf_token'],
					_form_filtr_abs['zcc_util'],
					_form_filtr_abs['zl_type_abs'],
					_form_filtr_abs['zl_annee'],
					_form_filtr_abs['zd_dt_deb_abs'],
					_form_filtr_abs['zd_dt_fin_abs'],
					_form_filtr_abs['zl_etat_abs'],
					_form_filtr_abs['rb_gby'] if 'rb_gby' in _form_filtr_abs else '',
					_form_filtr_abs['zcc_ajout_select_exist']
				)
			)]

			# Affichage du template
			output = render(_req, './real_etats/filtr_abs.html', {
				'dtab_filtr_abs' : form_filtr_abs.init_dtab(_req),
				'form_filtr_abs' : init_form(form_filtr_abs),
				'gby' : 'off' if _gby == False else 'on',
				'tab_fm' : tab_fm,
				'title' : title
			})

	else :

		# Soumission du formulaire
		form_filtr_abs = FiltrerAbsences(_req.POST, prefix = pref_filtr_abs, kw_gby = _gby, kw_util = obj_util)

		# Rafraîchissement de la datatable ou affichage des erreurs
		if form_filtr_abs.is_valid() :
			output = prep_dtab(form_filtr_abs.init_dtab(_req), {
				'modal_id' : '#fm_filtr_abs', 'modal_id_action' : 'hide'
			})
		else :
			tab_errs = { '{0}-{1}'.format(pref_filtr_abs, cle) : val for cle, val in form_filtr_abs.errors.items() }
			output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

	return output