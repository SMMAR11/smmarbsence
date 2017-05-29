# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu à vignettes relatif au module de gestion des agents
_req : Objet "requête"
'''
@verif_acces('gest_agents')
def get_menu(_req) :

	# Imports
	from app.functions import get_menu
	from app.functions import init_menu_vign
	from app.functions import init_vign
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Mise en forme du menu à vignettes du module de gestion des agents
		menu = init_menu_vign([init_vign(
			elem, ['item_href', 'item_img', 'item_name']
		) for elem in get_menu(_req)['gest_agents']['mod_items'].values()], 3)

		# Affichage du template
		output = render(_req, './gest_agents/get_menu.html', { 'menu' : menu, 'title' : 'Gestion des agents' })

	return output

'''
Affichage du formulaire de gestion d'un agent ou traitement d'une requête quelconque
_req : Objet "requête"
_inst : Ajout ou modification d'une instance ?
'''
@verif_acces('gest_agents')
def ger_agent(_req, _inst = False) :

	# Imports
	from app.forms.gest_agents import GererAgent
	from app.functions import init_fm
	from app.functions import init_form
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.http import Http404
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from django.template.context_processors import csrf
	import json

	output = None

	# Tentative d'obtention d'une instance TUtilisateur (si page de modification en cours)
	if _inst == False :
		obj_util = None
	else :
		if 'id' in _req.GET :
			obj_util = get_object_or_404(TUtilisateur, pk = _req.GET['id'])
		else :
			raise Http404

	# Initialisation du préfixe de chaque formulaire
	pref_ger_agent = 'GererAgent'
	pref_modif_mdp_agent = 'ModifierMotDePasseAgent'

	if _req.method == 'GET' :

		# Initialisation de chaque formulaire
		form_ger_agent = GererAgent(prefix = pref_ger_agent, instance = obj_util)
		if _inst == True :
			form_modif_mdp_agent = init_form(
				GererAgent(prefix = pref_modif_mdp_agent, instance = obj_util, kw_modif_mdp_agent = True)
			)

		# Initialisation des fenêtres modales
		tab_fm = [init_fm('ger_agent', 'Ajouter un agent' if _inst == False else 'Modifier un agent')]
		if _inst == True :
			tab_fm += [init_fm(
				'modif_mdp',
				'Modifier le mot de passe',
				'''
				<form action="{0}" method="post" name="form_modif_mdp" onsubmit="trait_post(event);">
					<input name="csrfmiddlewaretoken" type="hidden" value="{1}">
					<div class="row">
						<div class="col-sm-6">{2}</div>
						<div class="col-sm-6">{3}</div>
					</div>
					<button class="center-block custom-btn green-btn" type="submit">Valider</button>
				</form>
				'''.format(
					'?id={}&action=modifier-mot-de-passe'.format(obj_util.get_pk()),
					csrf(_req)['csrf_token'],
					form_modif_mdp_agent['zs_password'],
					form_modif_mdp_agent['zs_password_bis']
				)
			)]

		# Affichage du template
		output = render(_req, './gest_agents/ger_agent.html', {
			'a' : obj_util,
			'form_ger_agent' : init_form(form_ger_agent),
			'tab_fm' : tab_fm,
			'title' : 'Ajouter un agent' if _inst == False else 'Modifier un agent'
		})

	else :

		# Préparation de paramètres
		tab_params = None
		if 'action' in _req.GET :
			if _req.GET['action'] == 'modifier-mot-de-passe' :
				obj_util_auth = TUtilisateur.objects.get(pk = _req.user.pk) if _req.user.is_authenticated() else None
				tab_params = [
					pref_modif_mdp_agent,
					True,
					'Le mot de passe de l\'agent __USERNAME__ a été modifié avec succès.',
					['index', []] if obj_util == obj_util_auth else ['consult_agent', ['__PK__']]
				]
		else :
			tab_params = [
				pref_ger_agent,
				False,
				'L\'agent __USERNAME__ a été {} avec succès.'.format('ajouté' if _inst == False else 'modifié'),
				['consult_agent', ['__PK__']]
			]

		if tab_params :

			# Soumission du formulaire
			form_ger_agent = GererAgent(
				_req.POST, prefix = tab_params[0], instance = obj_util, kw_modif_mdp_agent = tab_params[1]
			)

			if form_ger_agent.is_valid() :

				# Création/modification d'une instance TUtilisateur
				obj_util_valid = form_ger_agent.save()

				# Mise à jour des paramètres
				if len(tab_params[3][1]) > 0 and tab_params[3][1][0] == '__PK__' :
					tab_params[3][1] = [obj_util_valid.get_pk()]

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : tab_params[2].replace('__USERNAME__', str(obj_util_valid)),
						'redirect' : reverse(tab_params[3][0], args = tab_params[3][1])
					}}),
					content_type = 'application/json'
				)

			else :

				# Affichage des erreurs
				tab_errs = { '{0}-{1}'.format(tab_params[0], cle) : val for cle, val in form_ger_agent.errors.items() }
				output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

	return output

'''
Affichage des agents dont le compte est créé (dernière étape avant la consultation de l'un des comptes)
_req : Objet "requête"
'''
@verif_acces('gest_agents')
def chois_agent(_req) :

	# Imports
	from app.forms.gest_agents import FiltrerAgents
	from app.functions import init_form
	from app.functions import prep_dtab
	from app.models import TUtilisateur
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_filtr_agents = FiltrerAgents()

		# Affichage du template
		output = render(_req, './gest_agents/chois_agent.html', {
			'dtab_filtr_agents' : form_filtr_agents.init_dtab(_req),
			'form_filtr_agents' : init_form(form_filtr_agents),
			'title' : 'Choisir un agent'
		})

	else :

		# Soumission du formulaire
		form_filtr_agents = FiltrerAgents(_req.POST)

		# Rafraîchissement de la datatable ou affichage des erreurs
		if form_filtr_agents.is_valid() :
			output = prep_dtab(form_filtr_agents.init_dtab(_req))
		else :
			output = HttpResponse(
				json.dumps(form_filtr_agents.errors), content_type = 'application/json'
			)

	return output

'''
Affichage de la page de consultation d'un agent ou traitement d'une requête quelconque
_req : Objet "requête"
_a : Instance TUtilisateur
'''
@verif_acces('gest_agents')
def consult_agent(_req, _a) :

	# Imports
	from app.forms.gest_agents import TrierTransactionsCetAgent
	from app.form_templates import get_ft_ger_statut_util
	from app.form_templates import get_ft_ger_trans_cet_util
	from app.forms.gest_agents import GererStatutAgent
	from app.forms.gest_agents import GererTransactionCetAgent
	from app.functions import affich_dem_suppr
	from app.functions import init_consult
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import prep_dtab
	from app.functions import transform_bool
	from app.models import TStatutsUtilisateur
	from app.models import TTransactionsCetUtilisateur
	from app.models import TUtilisateur
	from datetime import date
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from django.template.context_processors import csrf
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_ajout_statut_agent = 'AjouterStatutAgent'
	pref_ajout_trans_cet_agent = 'AjouterTransactionCetAgent'
	pref_modif_statut_agent = 'ModifierStatutAgent'
	pref_modif_trans_cet_agent = 'ModifierTransactionCetAgent'

	# Tentative d'obtention d'une instance TUtilisateur
	obj_util = get_object_or_404(TUtilisateur, pk = _a)

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.objects.get(pk = _req.user.pk)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Initialisation du formulaire de mise à jour d'un statut agent
			if _req.GET['action'] == 'initialiser-formulaire-modification-statut-agent' and 'id' in _req.GET :

				# Initialisation du formulaire
				form_ger_statut_util = GererStatutAgent(
					prefix = pref_modif_statut_agent,
					instance = TStatutsUtilisateur.objects.get(pk = _req.GET['id']),
					kw_util = obj_util
				)

				# Affichage du formulaire
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'content' : get_ft_ger_statut_util(_req, form_ger_statut_util)
					}}),
					content_type = 'application/json'
				)

			# Affichage d'une demande de suppression d'un statut agent
			if _req.GET['action'] == 'supprimer-statut-agent-etape-1' and 'id' in _req.GET :

				# Stockage en session du statut agent à supprimer
				_req.session['statut_util__pk'] = _req.GET['id']

				# Affichage de la demande de suppression du statut agent
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'content' : affich_dem_suppr('?action=supprimer-statut-agent-etape-2', 'suppr_statut_util')
					}}),
					content_type = 'application/json'
				)

			# Suppression d'un statut agent
			if _req.GET['action'] == 'supprimer-statut-agent-etape-2' and 'statut_util__pk' in _req.session :
				
				# Suppression d'une instance TStatutsUtilisateur
				obj_util.get_statut_util_set().get(pk = _req.session['statut_util__pk']).delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'L\'agent {} a été modifié avec succès.'.format(obj_util),
						'redirect' : reverse('consult_agent', args = [obj_util.get_pk()])
					}}),
					content_type = 'application/json'
				)

			# Initialisation du formulaire de mise à jour d'une transaction sur un CET
			if _req.GET['action'] == 'initialiser-formulaire-modification-transaction-entrante-cet-agent' and \
			'id' in _req.GET :

				# Initialisation du formulaire
				form_ger_trans_cet_util = GererTransactionCetAgent(
					prefix = pref_modif_trans_cet_agent,
					instance = TTransactionsCetUtilisateur.objects.get(pk = _req.GET['id']),
					kw_util = obj_util,
					kw_util_connect = obj_util_connect
				)

				# Affichage du formulaire
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'content' : get_ft_ger_trans_cet_util(_req, form_ger_trans_cet_util)
					}}),
					content_type = 'application/json'
				)

			# Affichage d'une demande de suppression d'une transaction entrante sur le CET
			if _req.GET['action'] == 'supprimer-transaction-entrante-cet-agent-etape-1' and 'id' in _req.GET :

				# Stockage en session du statut agent à supprimer
				_req.session['trans_cet_util__pk'] = _req.GET['id']

				# Affichage de la demande de suppression d'une transaction entrante sur le CET
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'content' : affich_dem_suppr(
							'?action=supprimer-transaction-entrante-cet-agent-etape-2', 'suppr_trans_cet_util'
						)
					}}),
					content_type = 'application/json'
				)

			# Suppression d'une transaction entrante sur le CET
			if _req.GET['action'] == 'supprimer-transaction-entrante-cet-agent-etape-2' and \
			'trans_cet_util__pk' in _req.session :
				
				# Suppression d'une instance TTransactionsCetUtilisateur
				obj_util.get_trans_cet_util_set().get(pk = _req.session['trans_cet_util__pk']).delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : '''
						Le compte épargne temps de l'agent {} a été modifié avec succès.
						'''.format(obj_util),
						'redirect' : reverse('consult_agent', args = [obj_util.get_pk()])
					}}),
					content_type = 'application/json'
				)

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
				'en_act' : {
					'label' : 'L\'agent est-il en activité ?', 'value' : transform_bool(obj_util.get_en_act())
				},
				'first_name' : { 'label' : 'Prénom', 'value' : obj_util.get_first_name() },
				'gpe_util' : {
					'label' : 'Groupes d\'utilisateur',
					'value' : ', '.join([str(gu) for gu in obj_util.get_gpe_util().all()])
				},
				'is_active' : {
					'label' : 'Le compte est-il actif ?',
					'last_child' : True,
					'value' : transform_bool(obj_util.get_is_active())
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
			form_tri_trans_cet_util = TrierTransactionsCetAgent(kw_util = obj_util)

			# Initialisation des fenêtres modales
			tab_fm = [
				init_fm(
					'ajout_trans_cet_util',
					'Ajouter une transaction entrante',
					get_ft_ger_trans_cet_util(
						_req, GererTransactionCetAgent(
							prefix = pref_ajout_trans_cet_agent, kw_util = obj_util, kw_util_connect = obj_util_connect
						)
					)
				),
				init_fm(
					'ajout_statut_util',
					'Ajouter un statut agent',
					get_ft_ger_statut_util(
						_req, GererStatutAgent(prefix = pref_ajout_statut_agent, kw_util = obj_util)
					)
				),
				init_fm('consult_abs', 'Consulter les absences autorisées ou en attente', obj_util.get_tabl_abs()),
				init_fm('modif_statut_util', 'Modifier un statut agent'),
				init_fm('modif_trans_cet_util', 'Modifier une transaction entrante'),
				init_fm('suppr_statut_util', 'Êtes-vous sûr de vouloir supprimer définitivement le statut agent ?'),
				init_fm(
					'suppr_trans_cet_util',
					'Êtes-vous sûr de vouloir supprimer définitivement la transaction entrante ?'
				)
			]

			# Affichage du template
			output = render(_req, './gest_agents/consult_agent.html', {
				'a' : obj_util,
				'dtab_tri_trans_cet_util' : form_tri_trans_cet_util.init_dtab(_req),
				'form_tri_trans_cet_util' : init_form(form_tri_trans_cet_util),
				'tab_attrs_util' : init_consult(tab_attrs_util),
				'tab_decompt_util' : tab_decompt_util,
				'tab_fm' : tab_fm,
				'tab_statut_util' : tab_statut_util,
				'title' : 'Consulter un agent'
			})

	else :
		if 'action' in _req.GET :
			
			# Définition du préfixe du formulaire de gestion des statuts agent
			if _req.GET['action'] == 'ajouter-statut-agent' :
				prefix = pref_ajout_statut_agent
			elif _req.GET['action'] == 'modifier-statut-agent' :
				prefix = pref_modif_statut_agent
			else :
				prefix = None

			if prefix :

				# Stockage des données du formulaire
				val_pk = _req.POST.get('{}-zsc_pk'.format(prefix))

				# Soumission du formulaire
				form_ger_statut_util = GererStatutAgent(
					_req.POST,
					instance = TStatutsUtilisateur.objects.get(pk = val_pk) if val_pk else None,
					prefix = prefix,
					kw_util = obj_util
				)

				if form_ger_statut_util.is_valid() :

					# Création/modification d'une instance TStatutsUtilisateur
					obj_statut_util_valid = form_ger_statut_util.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : '''
							L'agent {} a été modifié avec succès.
							'''.format(obj_statut_util_valid.get_util()),
							'redirect' : reverse('consult_agent', args = [obj_statut_util_valid.get_util().get_pk()])
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					tab_errs = {
						'{0}-{1}'.format(prefix, cle) : val for cle, val in form_ger_statut_util.errors.items()
					}
					output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

			# Définition du préfixe du formulaire de gestion des transactions entrantes sur le CET agent
			if _req.GET['action'] == 'ajouter-transaction-entrante-cet-agent' :
				prefix = pref_ajout_trans_cet_agent
			elif _req.GET['action'] == 'modifier-transaction-entrante-cet-agent' :
				prefix = pref_modif_trans_cet_agent
			else :
				prefix = None

			if prefix :

				# Stockage des données du formulaire
				val_pk = _req.POST.get('{}-zsc_pk'.format(prefix))

				# Soumission du formulaire
				form_ger_trans_cet_util = GererTransactionCetAgent(
					_req.POST,
					instance = TTransactionsCetUtilisateur.objects.get(pk = val_pk) if val_pk else None,
					prefix = prefix,
					kw_util = obj_util,
					kw_util_connect = obj_util_connect
				)

				if form_ger_trans_cet_util.is_valid() :

					# Création/modification d'une instance TTransactionsCetUtilisateur
					obj_trans_cet_util_valid = form_ger_trans_cet_util.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : '''
							Le compte épargne temps de l'agent {} a été modifié avec succès.
							'''.format(obj_trans_cet_util_valid.get_util()),
							'redirect' : reverse(
								'consult_agent', args = [obj_trans_cet_util_valid.get_util().get_pk()]
							)
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					tab_errs = {
						'{0}-{1}'.format(prefix, cle) : val for cle, val in form_ger_trans_cet_util.errors.items()
					}
					output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

			# Traitement du cas où je dois rafraîchir la fiche CET d'un agent (altération du mode de tri)
			if _req.GET['action'] == 'trier-transactions-cet-agent' :

				# Soumission du formulaire
				form_tri_trans_cet_util = TrierTransactionsCetAgent(_req.POST, kw_util = obj_util)

				# Rafraîchissement de la datatable ou affichage des erreurs
				if form_tri_trans_cet_util.is_valid() :
					output = prep_dtab(form_tri_trans_cet_util.init_dtab(_req))
				else :
					output = HttpResponse(
						json.dumps(form_tri_trans_cet_util.errors), content_type = 'application/json'
					)

	return output