# coding: utf-8

'''
Affichage du template d'erreur 403
_req : Objet "requête"
'''
def handler_403(_req) :

	# Import
	from app.functions import set_handler

	return set_handler(_req, 403, 'L\'accès à cette page est interdit.')

'''
Affichage du template d'erreur 404
_req : Objet "requête"
'''
def handler_404(_req) :

	# Import
	from app.functions import set_handler

	return set_handler(_req, 403, 'La page que vous recherchez n\'existe pas ou a été déplacée.')

'''
Affichage du template d'erreur 500
_req : Objet "requête"
'''
def handler_500(_req) :

	# Import
	from app.functions import set_handler

	return set_handler(_req, 500, 'Erreur interne du serveur.')