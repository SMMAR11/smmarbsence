# coding: utf-8

'''
Affichage de la page principale ou traitement d'une requête quelconque
_req : Objet "requête"
'''
def index(_req) :

	# Imports
	from app.apps import AppConfig
	from app.forms.index import Authentifier
	from app.functions import get_menu
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import init_menu_vign
	from app.functions import init_vign
	from app.models import TUtilisateur
	from django.contrib.auth import authenticate
	from django.contrib.auth import login
	from django.contrib.auth import logout
	from django.urls import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_auth = 'Authentifier'

	# Tentative d'obtention d'une instance TUtilisateur
	obj_util = TUtilisateur.objects.get(pk = _req.user.pk) if _req.user.is_authenticated else None

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Déconnexion de la plateforme
			if _req.GET['action'] == 'logout' :

				# Désactivation du mode super-secrétaire
				if obj_util :
					setattr(obj_util, 'est_super_secr', False)
					obj_util.save()

				# Nettoyage des variables de session
				for cle in list(_req.session.keys()) : del _req.session[cle]

				# Fermeture de la session active
				logout(_req)

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Merci pour votre connexion sur la plateforme {}.'.format(AppConfig.verbose_name),
						'redirect' : reverse('index')
					}}),
					content_type = 'application/json'
				)

			# Activation du mode super-secrétaire
			if _req.GET['action'] == 'activer-mode-super-secretaire' :
				if obj_util and 'S' in obj_util.get_type_util__list() :

					# Mise à jour de l'instance
					setattr(obj_util, 'est_super_secr', True)
					obj_util.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'Vous venez d\'activer le mode super-secrétaire.',
							'redirect' : '__reload__'
						}}),
						content_type = 'application/json'
					)

			# Désactivation du mode super-secrétaire
			if _req.GET['action'] == 'desactiver-mode-super-secretaire' :
				if obj_util :

					# Mise à jour de l'instance
					setattr(obj_util, 'est_super_secr', False)
					obj_util.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'Vous venez de désactiver le mode super-secrétaire.',
							'redirect' : '__reload__'
						}}),
						content_type = 'application/json'
					)

		else :
			
			# Initialisation de chaque formulaire
			form_auth = Authentifier(prefix = pref_auth)

			# Mise en forme du menu principal à vignettes
			menu = init_menu_vign([
				init_vign(elem, ['mod_href', 'mod_img', 'mod_name']) for elem in get_menu(_req).values()
			], 3)

			# Initialisation des fenêtres modales
			if _req.user.is_authenticated :
				tab_fm = []
			else :
				tab_fm = [init_fm('login', 'Connexion à la plateforme {}'.format(AppConfig.verbose_name))]
				
			# Affichage du template
			output = render(_req, './index.html', {
				'form_auth' : init_form(form_auth),
				'menu' : menu,
				'tab_fm' : tab_fm,
				'title' : 'Accueil' if _req.user.is_authenticated else 'Identification'
			})

	else :

		# Connexion à la plateforme
		if 'action' in _req.GET and _req.GET['action'] == 'login' :

			# Soumission du formulaire
			form_auth = Authentifier(_req.POST, prefix = pref_auth)

			if form_auth.is_valid() :

				# Stockage des données du formulaire
				cleaned_data = form_auth.cleaned_data
				val_username = cleaned_data.get('zs_username')
				val_password = cleaned_data.get('zs_password')

				# Déclaration de la session
				login(_req, authenticate(username = val_username, password = val_password))

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Bienvenue sur la plateforme {}.'.format(AppConfig.verbose_name),
						'redirect' : reverse('index')
					}}),
					content_type = 'application/json'
				)

			else :

				# Affichage des erreurs
				tab_errs = { '{0}-{1}'.format(pref_auth, cle) : val for cle, val in form_auth.errors.items() }
				output = HttpResponse(json.dumps(tab_errs), content_type = 'application/json')

	return output