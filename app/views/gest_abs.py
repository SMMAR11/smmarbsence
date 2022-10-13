# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu à vignettes relatif au module de gestion des absences
_req : Objet "requête"
'''
@verif_acces('gest_abs')
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
		) for elem in get_menu(_req)['gest_abs']['mod_items'].values()], 2)

		# Affichage du template
		output = render(_req, './gest_abs/get_menu.html', { 'menu' : menu, 'title' : 'Gestion des absences' })

	return output

'''
Affichage du formulaire de gestion d'une absence ou traitement d'une requête quelconque
_req : Objet "requête"
_inst : Ajout ou modification d'une instance ?
'''
@verif_acces('gest_abs')
def ger_abs(_req) :

	# Imports
	from app.forms.gest_abs import GererAbsence
	from app.functions import init_fm
	from app.functions import init_form
	from app.models import TAbsence
	from app.models import TUtilisateur
	from django.urls import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_ger_abs = 'GererAbsence'

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	if _req.method == 'GET' :

		# Initialisation de chaque formulaire
		form_ger_abs = GererAbsence(prefix = pref_ger_abs, kw_util = obj_util)

		# Initialisation des fenêtres modales
		tab_fm = [init_fm('ger_abs', 'Ajouter une absence')]

		# Affichage du template
		output = render(_req, './gest_abs/ger_abs.html', {
			'form_ger_abs' : init_form(form_ger_abs),
			'tab_fm' : tab_fm,
			'title' : 'Ajouter une absence'
		})

	else :

		# Soumission du formulaire
		form_ger_abs = GererAbsence(
			_req.POST,
			_req.FILES,
			prefix = pref_ger_abs,
			kw_dt_abs_tranche = int(_req.POST.get('{}-rb_dt_abs_tranche'.format(pref_ger_abs))),
			kw_req = _req,
			kw_type_abs = _req.POST.get('{}-zl_type_abs'.format(pref_ger_abs)),
			kw_util = obj_util
		)

		if form_ger_abs.is_valid() :

			# Création/modification d'une instance TAbsence
			obj_abs_valid = form_ger_abs.save()

			# Affichage du message de succès
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'L\'absence a été émise avec succès.',
					'redirect' : reverse('consult_abs', args = [obj_abs_valid.get_pk()])
				}}),
				content_type = 'application/json'
			)

		else :

			# Affichage des erreurs
			tab_errs = { '{0}-{1}'.format(pref_ger_abs, cle) : val for cle, val in form_ger_abs.errors.items() }
			output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

	return output

'''
Affichage des absences (dernière étape avant la consultation de l'une d'entre elles)
_req : Objet "requête"
'''
@verif_acces('gest_abs')
def chois_abs(_req) :

	# Imports
	from app.forms.gest_abs import FiltrerAbsences
	from app.functions import init_form
	from app.functions import prep_dtab
	from app.models import TUtilisateur
	from datetime import date
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	if _req.method == 'GET' :
		
		# Initialisation du formulaire
		form_filtr_abs = FiltrerAbsences(kw_util = obj_util)

		# Affichage du template
		output = render(_req, './gest_abs/chois_abs.html', {
			'dtab_filtr_abs' : form_filtr_abs.init_dtab(_req),
			'form_filtr_abs' : init_form(form_filtr_abs),
			'title' : 'Choisir une absence'
		})

	else :

		# Soumission du formulaire
		form_filtr_abs = FiltrerAbsences(_req.POST, kw_util = obj_util)

		# Rafraîchissement de la datatable ou affichage des erreurs
		if form_filtr_abs.is_valid() :
			output = prep_dtab(form_filtr_abs.init_dtab(_req))
			
		else :
			output = HttpResponse(json.dumps(form_filtr_abs.errors), content_type = 'application/json')

	return output

'''
Affichage de la page de consultation d'une absence ou traitement d'une requête quelconque
_req : Objet "requête"
_a : Instance TAbsence
'''
@verif_acces('gest_abs')
def consult_abs(_req, _a) :

	# Imports
	from app.forms.gest_abs import InsererPieceJustificativeAbsence
	from app.forms.gest_abs import ModifierTypeAbsenceFinal
	from app.functions import affich_dem_suppr
	from app.functions import init_consult
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import transform_bool
	from app.models import TAbsence
	from app.models import TUtilisateur
	from django.urls import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from django.template.context_processors import csrf
	import json

	# Initialisation du préfixe de chaque formulaire
	pref_inser_pj_abs = 'InsererPieceJustificativeAbsence'
	pref_modif_type_abs_final = 'ModifierTypeAbsenceFinal'

	output = None

	# Tentative d'obtention d'une instance TUtilisateur
	obj_abs = get_object_or_404(TAbsence, pk = _a)

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	# Vérification du droit d'accès
	obj_abs.can_read(obj_util, False)

	# Stockage de booléens
	can_update_type_abs_final = obj_abs.can_update_type_abs_final(obj_util, True)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Affichage d'une demande de suppression d'une absence
			if _req.GET['action'] == 'supprimer-absence-etape-1' :
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'content' : affich_dem_suppr('?action=supprimer-absence-etape-2', 'suppr_abs')
					}}),
					content_type = 'application/json'
				)

			# Suppression d'une absence
			if _req.GET['action'] == 'supprimer-absence-etape-2' :

				# Vérification du droit de suppression
				obj_abs.can_delete(obj_util, False)

				# Suppression d'une instance TAbsence
				obj_abs.delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'L\'absence a été supprimée avec succès.',
						'redirect' : reverse('chois_abs')
					}}),
					content_type = 'application/json'
				)

		else :

			# Instance TVerificationAbsence
			o_verif_abs = obj_abs.get_verif_abs()

			# Préparation des attributs disponibles en consultation
			tab_attrs_abs = {
				'comm_abs' : { 'label' : 'Commentaire', 'value' : obj_abs.get_comm_abs() },
				'comm_verif_abs' : {
					'label' : 'Commentaire',
					'last_child' : True,
					'value' : o_verif_abs.get_comm_verif_abs() if o_verif_abs else None
				},
				'dt_abs' : { 'label' : 'Date de l\'absence', 'value' : obj_abs.get_dt_abs__fr_str() },
				'dt_emiss_abs' : { 'label' : 'Date d\'émission de l\'absence', 'value' : obj_abs.get_dt_emiss_abs__str() },
				'dt_verif_abs' : {
					'label' : 'Date de vérification de l\'absence',
					'value' : o_verif_abs.get_dt_verif_abs__str() if o_verif_abs else None
				},
				'est_autor' : {
					'label' : 'L\'absence est-elle autorisée ?',
					'value' : transform_bool(o_verif_abs.get_est_autor()) if o_verif_abs else None
				},
				'pj_abs' : {
					'label' : 'Consulter le justificatif d\'absence', 'value' : obj_abs.get_pj_abs__path(), 'pdf' : True
				},
				'id_util_connect' : {
					'label' : 'Agent ayant émis l\'absence',
					'value' : obj_abs.get_util_connect().get_nom_complet() if obj_abs.get_util_connect() else None
				},
				'id_util_emett' : { 'label' : 'Agent concerné', 'value' : obj_abs.get_util_emett().get_nom_complet() },
				'id_util_verif' : {
					'label' : 'Agent ayant vérifié l\'absence',
					'value' : o_verif_abs.get_util_verif().get_nom_complet()
					if o_verif_abs and o_verif_abs.get_util_verif() else None
				},
				'id_type_abs' : { 'label' : 'Type de l\'absence', 'value' : obj_abs.get_type_abs() },
				'id_type_abs_final' : {
					'label' : 'Type final de l\'absence',
					'value' : o_verif_abs.get_type_abs_final() if o_verif_abs else None
				},
				'num_annee' : { 'label' : 'Année', 'value' : obj_abs.get_annee() }
			}

			# Initialisation des fenêtres modales
			tab_fm = [init_fm('suppr_abs', 'Êtes-vous sûr de vouloir supprimer définitivement l\'absence ?')]

			# Initialisation des actions supplémentaires
			tab_act = []

			if obj_abs.can_update_pj_abs(obj_util, True) == True :

				# Initialisation du formulaire
				form_inser_pj_abs = init_form(InsererPieceJustificativeAbsence(
					prefix = pref_inser_pj_abs, instance = obj_abs
				))

				# Empilement des actions supplémentaires
				tab_act.append(
					'''
					<span class="icon-with-text iwt-c-white pdf-icon" data-target="#fm_inser_pj_abs" data-toggle="modal">
						Insérer le justificatif d'absence
					</span>
					'''
				)

				# Agrandissement du tableau des fenêtres modales
				tab_fm += [init_fm(
					'inser_pj_abs',
					'Insérer le justificatif d\'absence',
					'''
					<form action="?action=inserer-piece-justificative-absence" enctype="multipart/form-data" 
					method="post" name="form_inser_pj_abs" onsubmit="trait_post(event);">
						<input name="csrfmiddlewaretoken" type="hidden" value="{0}">
						{1}
						<button class="center-block custom-btn green-btn" type="submit">Valider</button>
					</form>
					'''.format(csrf(_req)['csrf_token'], form_inser_pj_abs['zu_pj_abs'])
				)]

			if can_update_type_abs_final == True :

				# Initialisation du formulaire
				form_modif_type_abs_final = init_form(ModifierTypeAbsenceFinal(
					prefix = pref_modif_type_abs_final, instance = o_verif_abs
				))

				# Agrandissement du tableau des fenêtres modales
				tab_fm += [init_fm(
					'modif_type_abs_final',
					'Modifier le type final de l\'absence',
					'''
					<form action="?action=modifier-type-absence-final" method="post" name="form_modif_type_abs_final"
					onsubmit="trait_post(event);">
						<input name="csrfmiddlewaretoken" type="hidden" value="{0}">
						{1}
						<button class="center-block custom-btn green-btn" type="submit">Valider</button>
					</form>
					'''.format(csrf(_req)['csrf_token'], form_modif_type_abs_final['zl_type_abs_final'])
				)]

			if obj_abs.can_delete(obj_util, True) == True :

				# Empilement des actions supplémentaires
				tab_act.append(
					'''
					<span action="?action=supprimer-absence-etape-1" class="delete-icon icon-with-text iwt-c-white"
					onclick="trait_get(event, 'suppr_abs');">
						Supprimer
					</span>
					'''
				)

			# Affichage du template
			output = render(_req, './gest_abs/consult_abs.html', {
				'a' : obj_abs,
				'can_update_type_abs_final' : can_update_type_abs_final,
				'tab_act' : tab_act,
				'tab_attrs_abs' : init_consult(tab_attrs_abs),
				'tab_fm' : tab_fm,
				'title' : 'Consulter une absence'
			})

	else :
		if 'action' in _req.GET :

			# Insertion de la pièce justificative de l'absence
			if _req.GET['action'] == 'inserer-piece-justificative-absence' :

				# Application du droit de modification
				obj_abs.can_update_pj_abs(obj_util, False)

				# Soumission du formulaire
				form_inser_pj_abs = InsererPieceJustificativeAbsence(
					_req.POST, _req.FILES, prefix = pref_inser_pj_abs, instance = obj_abs
				)

				if form_inser_pj_abs.is_valid() :

					# Mise à jour d'une instance TAbsence
					obj_abs_valid = form_inser_pj_abs.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'L\'absence a été mise à jour avec succès.',
							'redirect' : reverse('consult_abs', args = [obj_abs_valid.get_pk()])
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					tab_errs = { '{0}-{1}'.format(
						pref_inser_pj_abs, cle
					) : val for cle, val in form_inser_pj_abs.errors.items() }
					output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

			# Modification du type final d'une absence
			if _req.GET['action'] == 'modifier-type-absence-final' :

				# Application du droit de modification
				obj_abs.can_update_type_abs_final(obj_util, False)

				# Soumission du formulaire
				form_modif_type_abs_final = ModifierTypeAbsenceFinal(
					_req.POST, prefix = pref_modif_type_abs_final, instance = obj_abs.get_verif_abs()
				)

				if form_modif_type_abs_final.is_valid() :

					# Mise à jour d'une instance TVerificationAbsence
					obj_verif_abs_valid = form_modif_type_abs_final.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'L\'absence a été mise à jour avec succès.',
							'redirect' : reverse('consult_abs', args = [obj_verif_abs_valid.get_pk()])
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					tab_errs = { '{0}-{1}'.format(
						pref_modif_type_abs_final, cle
					) : val for cle, val in form_modif_type_abs_final.errors.items() }
					output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

	return output

'''
Affichage de la page de choix d'une absence à vérifier ou traitement d'une requête quelconque
_req : Objet "requête"
'''
@verif_acces('gest_abs', 'verif_abs')
def chois_verif_abs(_req) :

	# Imports
	from app.forms.gest_abs import FiltrerVerificationAbsences
	from app.functions import init_form
	from app.functions import prep_dtab
	from app.models import TUtilisateur
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_filtr_verif_abs = FiltrerVerificationAbsences(kw_util = obj_util)

		# Affichage du template
		output = render(_req, './gest_abs/chois_verif_abs.html', {
			'dtab_filtr_verif_abs' : form_filtr_verif_abs.init_dtab(_req),
			'form_filtr_verif_abs' : init_form(form_filtr_verif_abs),
			'title' : 'Choisir une absence en attente'
		})

	else :

		# Soumission du formulaire
		form_filtr_verif_abs = FiltrerVerificationAbsences(_req.POST, kw_util = obj_util)

		# Rafraîchissement de la datatable ou affichage des erreurs
		if form_filtr_verif_abs.is_valid() :
			output = prep_dtab(form_filtr_verif_abs.init_dtab(_req))
			
		else :
			output = HttpResponse(json.dumps(form_filtr_verif_abs.errors), content_type = 'application/json')

	return output

'''
Affichage de la page de vérification d'une absence ou traitement d'une requête quelconque
_req : Objet "requête"
_a : Instance TAbsence
'''
@verif_acces('gest_abs', 'verif_abs')
def verif_abs(_req, _a) :

	# Imports
	from app.forms.gest_abs import VerifierAbsence
	from app.functions import get_obj_dt
	from app.functions import init_consult
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import transform_bool
	from app.models import TAbsence
	from app.models import TDatesAbsence
	from app.models import TUtilisateur
	from django.conf import settings
	from django.core.exceptions import PermissionDenied
	from django.urls import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_verif_abs = 'VerifierAbsence'

	# Tentative d'obtention d'une instance TAbsence
	obj_abs = get_object_or_404(TAbsence, pk = _a)

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	# Vérification des droits d'accès
	if obj_abs not in obj_util.get_abs_a_verif__list() : raise PermissionDenied

	'''
	Obtention du nombre de jours d'absence déjà autorisés pour le type d'absence lié à une absence
	_obj : Instance TAbsence
	_code : Par mois ou par année ?
	Retourne un tableau associatif
	'''
	def calc_nbre_j(_obj, _code) :

		# Import
		from app.models import TDatesAbsence

		output = {}

		# Initialisation du tableau des dates d'absence
		tab_dt_abs = [[da.get_dt_abs(), da.get_indisp_dt_abs()] for da in _obj.get_dt_abs_set().all()]

		# Groupement d'objets "date"
		if _code == 'MOIS' :
			tab_dt_abs__group_by = [
				[j for j in tab_dt_abs if '{0}_{1}'.format(j[0].month, j[0].year) == i] for i in set(
					map(lambda l : '{0}_{1}'.format(l[0].month, l[0].year), tab_dt_abs)
				)
			]
		elif _code == 'ANNEE' :
			tab_dt_abs__group_by = [[j for j in tab_dt_abs if j[0].year == i] for i in set(
				map(lambda l : l[0].year, tab_dt_abs)
			)]
		else :
			tab_dt_abs__group_by = []

		for elem in tab_dt_abs__group_by :

			# Stockage du mois et de l'année
			mois = elem[0][0].month
			annee = elem[0][0].year

			# Définition des conditions de la requête
			if _code == 'MOIS' :
				tab_filter = {
					'dt_abs__month' : mois, 'dt_abs__year' : annee, 'id_abs__id_util_emett' : _obj.get_util_emett()
				}
			else :
				tab_filter = { 'id_abs__num_annee' : annee, 'id_abs__id_util_emett' : _obj.get_util_emett() }

			# Initialisation du nombre de jours déjà autorisés
			nbre_j = 0

			# Cumul du nombre de jours déjà autorisés
			for da in TDatesAbsence.objects.filter(**tab_filter) :
				obj_verif_abs = da.get_abs().get_verif_abs()
				if obj_verif_abs :
					if obj_verif_abs.get_type_abs_final() == _obj.get_type_abs() :
						if da.get_abs().get_etat_abs() == 1 :
							if da.get_indisp_dt_abs() == 'WD' :
								nbre_j += 1
							else :
								nbre_j += 0.5

			# Empilement du tableau de sortie
			output['{0}_{1}'.format(mois, annee) if _code == 'MOIS' else str(annee)] = nbre_j

		return output

	if _req.method == 'GET' :

		# Préparation des attributs disponibles en consultation (onglet 1)
		tab_attrs_abs = {
			'comm_abs' : { 'label' : 'Commentaire', 'last_child' : True, 'value' : obj_abs.get_comm_abs() },
			'dt_abs' : { 'label' : 'Date de l\'absence', 'value' : obj_abs.get_dt_abs__fr_str() },
			'pj_abs' : {
				'label' : 'Consulter le justificatif d\'absence', 'value' : obj_abs.get_pj_abs__path(), 'pdf' : True
			},
			'id_util_emett' : { 'label' : 'Agent concerné', 'value' : obj_abs.get_util_emett().get_nom_complet() },
			'id_type_abs' : { 'label' : 'Type de l\'absence', 'value' : obj_abs.get_type_abs() },
			'num_annee' : { 'label' : 'Année', 'value' : obj_abs.get_annee() }
		}

		# Préparation des données relatives au nombre de jours d'absence déjà autorisés
		tab_nbre_j_abs_annee = [[int(cle), val] for cle, val in calc_nbre_j(obj_abs, 'ANNEE').items()]
		tab_nbre_j_abs_mois = [[
			int(cle.split('_')[0]),
			get_obj_dt('MONTHS')[int(cle.split('_')[0]) - 1],
			int(cle.split('_')[1]),
			val
		] for cle, val in calc_nbre_j(obj_abs, 'MOIS').items()]

		# Vérification d'un quelconque conflit entre plusieurs absences
		conflit = False
		for daa in obj_abs.get_dt_abs_set().all() :
			for da in TDatesAbsence.objects.filter(
				dt_abs = daa.get_dt_abs(), id_abs__id_util_emett = obj_abs.get_util_emett()
			) :
				if da.get_abs().get_etat_abs() == 1 :
					if da.get_indisp_dt_abs() == 'WD' :
						conflit = True
					elif da.get_indisp_dt_abs() == 'AM' :
						if daa.get_indisp_dt_abs() != 'PM' : conflit = True
					elif da.get_indisp_dt_abs() == 'PM' :
						if daa.get_indisp_dt_abs() != 'AM' : conflit = True

		# Préparation des attributs disponibles en consultation (onglet 2)
		tab_attrs_aide = {
			'conflit_abs' : {
				'label' : 'Une absence est-elle déjà autorisée pendant cette absence ?',
				'last_child' : True,
				'value' : transform_bool(conflit)
			},
			'descr_nds_type_abs' : { 
				'label' : '''
				Extrait de la note de service pour le type d'absence suivant : « {} »
				'''.format(obj_abs.get_type_abs()),
				'value' : obj_abs.get_type_abs().get_descr_nds_type_abs()
			},
			'nbre_j_abs_annee' : {
				'datatable' : True,
				'datatable_header' : 'Année|Nombre de jours déjà autorisés',
				'label' : '''
				Nombre de jours déjà autorisés par année pour le type d'absence suivant : « {} »
				'''.format(obj_abs.get_type_abs()),
				'value' : list(sorted(tab_nbre_j_abs_annee, key = lambda l : l[0]))
			},
			'nbre_j_abs_mois' : {
				'datatable' : True,
				'datatable_header' : 'Mois|Année|Nombre de jours déjà autorisés',
				'label' : '''
				Nombre de jours déjà autorisés par période pour le type d'absence suivant : « {} »
				'''.format(obj_abs.get_type_abs()),
				'value' : [elem[1:] for elem in list(sorted(tab_nbre_j_abs_mois, key = lambda l : (l[2], l[0])))]
			} 
		}

		# Ajout d'un attribut d'aide en cas de vérification d'une absence dont le groupe de type d'absence est "CET"
		if obj_abs.get_type_abs().get_gpe_type_abs().get_pk() == settings.DB_PK_DATAS['CET_PK'] :
			tab_attrs_aide['solde_cet_restant_util'] = {
				'label' : 'Solde restant prévisionnel sur le compte épargne temps (CET)',
				'value' : obj_abs.get_util_emett().get_solde_cet_restant_util__str(
					obj_abs.get_util_emett().get_solde_cet_util() - obj_abs.get_nbre_dt_abs()
				)
			}

		# Initialisation du formulaire
		form_verif_abs = VerifierAbsence(prefix = pref_verif_abs)

		# Initialisation des fenêtres modales
		tab_fm = [init_fm('verif_abs', 'Vérifier une absence')]

		# Affichage du template
		output = render(_req, './gest_abs/verif_abs.html', {
			'form_verif_abs' : init_form(form_verif_abs),
			'tab_attrs_abs' : init_consult(tab_attrs_abs),
			'tab_attrs_aide' : init_consult(tab_attrs_aide),
			'tab_fm' : tab_fm,
			'title' : 'Vérifier une absence'
		})

	else :

		# Soumission du formulaire
		form_verif_abs = VerifierAbsence(
			_req.POST, prefix = pref_verif_abs, kw_abs = obj_abs, kw_req = _req, kw_util_connect = obj_util
		)

		if form_verif_abs.is_valid() :

			# Création d'une instance TVerificationAbsence
			obj_verif_abs_valid = form_verif_abs.save()

			# Affichage du message de succès
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'L\'absence a été vérifiée avec succès.',
					'redirect' : reverse('consult_abs', args = [obj_verif_abs_valid.get_pk()])
				}}),
				content_type = 'application/json'
			)

		else :

			# Affichage des erreurs
			tab_errs = { '{0}-{1}'.format(pref_verif_abs, cle) : val for cle, val in form_verif_abs.errors.items() }
			output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

	return output