# coding: utf-8

# Import
from app.decorators import *

'''
Affichage des messages ou traitement d'une requête quelconque
_req : Objet "requête"
'''
@verif_acces()
def get_mess(_req) :

	# Imports
	from app.forms.mess import SelectionnerMessages
	from app.functions import affich_dem_suppr
	from app.functions import init_fm
	from app.functions import init_form
	from app.models import TMessagesUtilisateur
	from app.models import TUtilisateur
	from django.urls import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_select_mess_bdr = 'SelectionnerMessagesBdR'
	pref_select_mess_arch = 'SelectionnerMessagesArchives'

	# Obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Suppression des messages sélectionnés
			if _req.GET['action'] == 'supprimer-messages-etape-2' :

				# Stockage des messages à supprimer
				qs_mess_a_suppr = TMessagesUtilisateur.objects.filter(pk__in = _req.session['tab_mess_a_suppr'])

				# Suppression de la variable de session stockant les identifiants des instances TMessagesUtilisateur à
				# supprimer
				del _req.session['tab_mess_a_suppr']

				# Préparation du message de succès
				if qs_mess_a_suppr.count() > 1 :
					mess = 'Les messages sélectionnés ont été supprimés avec succès.'
				else :
					mess = 'Le message sélectionné a été supprimé avec succès.'
				
				# Suppression de certaines instances TMessagesUtilisateur
				for mu in qs_mess_a_suppr : mu.delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : { 'message' : mess, 'redirect' : reverse('get_mess') }}),
					content_type = 'application/json'
				)

		else :

			# Initialisation de chaque formulaire
			form_select_mess_bdr = SelectionnerMessages(prefix = pref_select_mess_bdr, kw_util = obj_util)
			form_select_mess_arch = SelectionnerMessages(
				prefix = pref_select_mess_arch, kw_util = obj_util, kw_est_arch = True
			)

			# Initialisation de la variable de session stockant les identifiants des instances TMessagesUtilisateur à
			# supprimer
			_req.session['tab_mess_a_suppr'] = []

			# Initialisation des fenêtres modales
			tab_fm = [init_fm(
				'suppr_mess', 'Êtes-vous sûr de vouloir supprimer définitivement les messages sélectionnés ?'
			)]

			# Affichage du template
			output = render(_req, './mess/get_mess.html', {
				'form_select_mess_arch' : init_form(form_select_mess_arch),
				'form_select_mess_bdr' : init_form(form_select_mess_bdr),
				'qs_mess_util_arch__count' : obj_util.get_mess_util_set__count(True),
				'qs_mess_util_bdr__count' : obj_util.get_mess_util_set__count(False),
				'tab_fm' : tab_fm,
				'title' : 'Messages'
			})

	else :
		if 'action' in _req.GET :
			get_action = _req.GET['action']

			# Déplacement des messages sélectionnés
			if get_action == 'deplacer-vers' :
				if 'ou' in _req.GET :
					get_ou = _req.GET['ou']

					# Préparation de paramètres
					tab_params = None
					if get_ou == 'messages-archives' :
						tab_params = [pref_select_mess_bdr, False, True]
					if get_ou == 'boite-de-reception' :
						tab_params = [pref_select_mess_arch, True, False]

					if tab_params :

						# Soumission du formulaire
						form_select_mess = SelectionnerMessages(
							_req.POST, prefix = tab_params[0], kw_util = obj_util, kw_est_arch = tab_params[1]
						)

						if form_select_mess.is_valid() :

							# Stockage des données du formulaire
							cleaned_data = form_select_mess.cleaned_data
							val_mess_util = cleaned_data.get('zcc_mess_util')

							# Mise à jour de certaines instances TMessagesUtilisateur
							TMessagesUtilisateur.objects.filter(pk__in = val_mess_util).update(
								est_arch = tab_params[2]
							)

							# Affichage du message de succès
							output = HttpResponse(
								json.dumps({ 'success' : { 'redirect' : reverse('get_mess') }}),
								content_type = 'application/json'
							)

						else :

							# Affichage des erreurs
							tab_errs = { '{0}-{1}'.format(
								tab_params[0], cle
							) : val for cle, val in form_select_mess.errors.items() }
							output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

			# Affichage d'une demande de suppression des messages sélectionnés
			if get_action == 'supprimer-messages-etape-1' :
				if 'depuis' in _req.GET :
					get_depuis = _req.GET['depuis']

					# Préparation de paramètres
					tab_params = None
					if get_depuis == 'boite-de-reception' :
						tab_params = [pref_select_mess_bdr, False]
					if get_depuis == 'messages-archives' :
						tab_params = [pref_select_mess_arch, True]

					if tab_params :

						# Soumission du formulaire.
						form_select_mess = SelectionnerMessages(
							_req.POST, prefix = tab_params[0], kw_util = obj_util, kw_est_arch = tab_params[1]
						)

						if form_select_mess.is_valid() :

							# Stockage des données du formulaire
							cleaned_data = form_select_mess.cleaned_data
							val_mess_util = cleaned_data.get('zcc_mess_util')

							# Préparation de la variable de session stockant les identifiants des instances
							# TMessagesUtilisateur à supprimer
							_req.session['tab_mess_a_suppr'] = val_mess_util

							# Affichage de la demande de suppression des messages sélectionnés
							output = HttpResponse(
								json.dumps({ 'success' : { 
									'content' : affich_dem_suppr('?action=supprimer-messages-etape-2', 'suppr_mess')
								}}),
								content_type = 'application/json'
							)

						else :

							# Affichage des erreurs
							tab_errs = { '{0}-{1}'.format(
								tab_params[0], cle
							) : val for cle, val in form_select_mess.errors.items() }
							output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

	return output

'''
Consultation d'un message ou traitement d'une requête quelconque
_req : Objet "requête"
_mu : Instance TMessagesUtilisateur
'''
@verif_acces()
def consult_mess(_req, _mu) :

	# Imports
	from app.functions import affich_dem_suppr
	from app.functions import init_consult
	from app.functions import init_fm
	from app.models import TMessagesUtilisateur
	from django.urls import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import redirect
	from django.shortcuts import render
	import json

	output = None

	# Tentative d'obtention d'une instance TMessagesUtilisateur
	obj_mess_util = get_object_or_404(TMessagesUtilisateur, pk = _mu)

	if _req.method == 'GET' :
		if 'action' in _req.GET :
			get_action = _req.GET['action']

			# Archivage d'un message
			if get_action == 'archiver' :

				# Mise à jour d'une instance TMessagesUtilisateur
				if obj_mess_util.get_est_arch() == False :
					setattr(obj_mess_util, 'est_arch', True)
					obj_mess_util.save()

				# Redirection
				output = redirect('get_mess')

			# Déplacement d'un message vers la boîte de réception
			if get_action == 'deplacer' :

				# Mise à jour d'une instance TMessagesUtilisateur
				if obj_mess_util.get_est_arch() == True :
					setattr(obj_mess_util, 'est_arch', False)
					obj_mess_util.save()

				# Redirection
				output = redirect('get_mess')

			# Affichage d'une demande de suppression d'un message
			if get_action == 'supprimer-message-etape-1' :
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'content' : affich_dem_suppr('?action=supprimer-message-etape-2', 'suppr_mess_util')
					}}),
					content_type = 'application/json'
				)

			# Suppression d'un message
			if get_action == 'supprimer-message-etape-2' :

				# Suppression d'une instance TMessagesUtilisateur
				obj_mess_util.delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le message a été supprimé avec succès.', 'redirect' : reverse('get_mess')
					}}),
					content_type = 'application/json'
				)

		else :

			# Mise à jour d'une instance TMessagesUtilisateur
			if obj_mess_util.get_est_lu() == False :
				setattr(obj_mess_util, 'est_lu', True)
				obj_mess_util.save()

			# Préparation des attributs disponibles en consultation
			tab_attrs_mess = {
				'corps_mess' : {
					'label' : 'Message', 'last_child' : True, 'value' : obj_mess_util.get_mess().get_corps_mess()
				},
				'dt_mess' : { 'label' : 'Reçu le', 'value' : obj_mess_util.get_mess().get_dt_mess__str() },
				'exped_mess' : { 'label' : 'De', 'value' : obj_mess_util.get_mess().get_emett_mess() },
				'obj_mess' : { 'label' : 'Objet', 'value' : obj_mess_util.get_mess().get_obj_mess() }
			}

			# Initialisation des fenêtres modales
			tab_fm = [init_fm('suppr_mess_util', 'Êtes-vous sûr de vouloir supprimer définitivement le message ?')]

			# Affichage du template
			output = render(_req, './mess/consult_mess.html', {
				'mu' : obj_mess_util,
				'tab_attrs_mess' : init_consult(tab_attrs_mess),
				'tab_fm' : tab_fm,
				'title' : 'Consulter un message'
			})

	return output