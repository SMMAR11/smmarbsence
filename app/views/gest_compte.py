# coding: utf-8

# Import
from app.decorators import *

'''
Affichage de la page de consultation du compte de l'agent connecté à la plateforme SMMARbsence
_req : Objet "requête"
'''
@verif_acces('gest_compte')
def consult_compte(_req) :

	# Imports
	from app.forms.gest_agents import TrierTransactionsCetAgent
	from app.functions import init_consult
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import prep_dtab
	from app.functions import transform_bool
	from app.models import TUtilisateur
	from datetime import date
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Téléchargement de la fiche CET d'un agent
			if _req.GET['action'] == 'telecharger-cet-agent' and 'mode-de-tri' in _req.GET and \
			'historique' in _req.GET :
				hist_trans_cet_util = _req.GET['historique']
				if hist_trans_cet_util : hist_trans_cet_util = int(hist_trans_cet_util)
				output = obj_util.get_fiche_cet(_req.GET['mode-de-tri'], hist_trans_cet_util)

			# Affichage des absences autorisées ou en attente
			if _req.GET['action'] == 'consulter-absences' and 'annee' in _req.GET :
				output = prep_dtab(obj_util.get_tabl_abs(_req.GET['annee']), {
					'modal_id' : '#fm_consult_abs', 'modal_id_action' : 'show'
				})

		else :

			# Préparation des attributs disponibles en consultation
			tab_attrs_util = {
				'courr_second_util' : { 'label' : 'Courriel secondaire', 'value' : obj_util.get_courr_second_util() },
				'email' : { 'label' : 'Courriel principal', 'value' : obj_util.get_email() },
				'email_auto_courr_princ' : {
					'label' : 'Les notifications sont-elles envoyées sur le courriel principal ?',
					'value' : transform_bool(obj_util.get_email_auto_courr_princ())
				},
				'email_auto_courr_second' : {
					'label' : 'Les notifications sont-elles envoyées sur le courriel secondaire ?',
					'value' : transform_bool(obj_util.get_email_auto_courr_second())
				},
				'en_act' : { 'label' : 'Êtes-vous en activité ?', 'value' : transform_bool(obj_util.get_en_act()) },
				'first_name' : { 'label' : 'Prénom', 'value' : obj_util.get_first_name() },
				'gpe_util' : {
					'label' : 'Groupes d\'utilisateur',
					'value' : ', '.join([str(gu) for gu in obj_util.get_gpe_util().all()])
				},
				'last_name' : { 'label' : 'Nom de famille', 'value' : obj_util.get_last_name() },
				'solde_cet_util' : {
					'label' : 'Solde restant sur le compte épargne temps (CET)',
					'value' : obj_util.get_solde_cet_restant_util__str()
				},
				'type_util' : {
					'label' : 'Quels sont les rôles assignés au compte ?',
					'value' : ', '.join([str(tu) for tu in obj_util.get_type_util().all()])
				},
				'username' : { 'label' : 'Nom d\'utilisateur', 'value' : obj_util.get_username() }
			}

			# Initialisation des statuts agent
			tab_statut_util = []
			for su in obj_util.get_statut_util_set().all() :

				# Détermination du statut agent actuel
				statut_util_actuel = False
				if date.today() > date(su.get_annee().get_pk(), su.get_mois_deb_statut_util(), 1) :
					statut_util_actuel = True
					for elem in tab_statut_util :
						if elem['class'] : elem['class'] = None

				tab_statut_util.append({
					'class' : 'to-highlight' if statut_util_actuel == True else None,
					'period_deb_statut_util' : su.get_period_deb_statut_util(),
					'pk' : su.get_pk(),
					'statut_util' : su.get_statut_util__str()
				})

			# Initialisation des décomptes agent
			tab_decompt_util = [{
				'annee' : du.get_annee(),
				'nbre_j_cp_autor' : du.get_util().get_nbre_j_autor__str(True, du.get_annee().get_pk()),
				'nbre_j_cp_base' : du.get_nbre_j_cp_base__str(),
				'nbre_j_cp_rest' : du.get_util().get_nbre_j_rest__str(True, du.get_annee().get_pk()),
				'nbre_j_cp_transf' : du.get_util().get_nbre_j_transf__str(True, du.get_annee().get_pk()),
				'nbre_j_rtt_autor' : du.get_util().get_nbre_j_autor__str(False, du.get_annee().get_pk()),
				'nbre_j_rtt_base' : du.get_nbre_j_rtt_base__str(),
				'nbre_j_rtt_rest' : du.get_util().get_nbre_j_rest__str(False, du.get_annee().get_pk()),
				'nbre_j_rtt_transf' : du.get_util().get_nbre_j_transf__str(False, du.get_annee().get_pk()),
			} for du in obj_util.get_decompt_util_set().reverse()]

			# Initialisation du formulaire de tri des transactions d'un CET
			form_tri_trans_cet_util = TrierTransactionsCetAgent(kw_consult = True, kw_util = obj_util)

			# Affichage du template
			output = render(_req, './gest_compte/consult_compte.html', {
				'dtab_tri_trans_cet_util' : form_tri_trans_cet_util.init_dtab(_req),
				'form_tri_trans_cet_util' : init_form(form_tri_trans_cet_util),
				'tab_attrs_util' : init_consult(tab_attrs_util),
				'tab_decompt_util' : tab_decompt_util,
				'tab_fm' : [init_fm(
					'consult_abs', 'Consulter les absences autorisées ou en attente', obj_util.get_tabl_abs()
				)],
				'tab_statut_util' : tab_statut_util,
				'title' : 'Consulter mon compte',
			})

	else :

		# Traitement du cas où je dois rafraîchir la fiche CET d'un agent (altération du mode de tri)
		if _req.GET['action'] == 'trier-transactions-cet-agent' :

			# Soumission du formulaire
			form_tri_trans_cet_util = TrierTransactionsCetAgent(_req.POST, kw_consult = True, kw_util = obj_util)

			# Rafraîchissement de la datatable ou affichage des erreurs
			if form_tri_trans_cet_util.is_valid() :
				output = prep_dtab(form_tri_trans_cet_util.init_dtab(_req))
			else :
				output = HttpResponse(json.dumps(form_tri_trans_cet_util.errors), content_type = 'application/json')

	return output

'''
Affichage de la page de modification du compte de l'agent connecté à la plateforme SMMARbsence ou traitement d'une
requête quelconque
_req : Objet "requête"
'''
@verif_acces('gest_compte')
def modif_compte(_req) :

	# Imports
	from app.forms.gest_compte import ModifierCompte
	from app.functions import init_fm
	from app.functions import init_form
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	if _req.method == 'GET' :

		# Affichage du template
		output = render(_req, './gest_compte/modif_compte.html', {
			'form_modif_compte' : init_form(ModifierCompte(instance = obj_util)),
			'tab_fm' : [init_fm('modif_compte', 'Modifier mon compte')],
			'title' : 'Modifier mon compte',
			'u' : obj_util
		})

	else :

		# Soumission du formulaire
		form_modif_compte = ModifierCompte(_req.POST, instance = obj_util)

		if form_modif_compte.is_valid() :

			# Modification d'une instance TUtilisateur
			obj_util_valid = form_modif_compte.save()

			# Affichage du message de succès
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'Votre compte a été mis à jour avec succès.', 'redirect' : reverse('consult_compte')
				}}),
				content_type = 'application/json'
			)

		else :

			# Affichage des erreurs
			output = HttpResponse(json.dumps(form_modif_compte.errors), content_type = 'application/json')

	return output