# coding: utf-8

# Import
from app.decorators import *

'''
Affichage des alertes
_req : Objet "requête"
'''
@verif_acces()
def get_alert(_req) :

	# Import
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Affichage du template
		output = render(_req, './alert/get_alert.html', { 'title' : 'Alertes' })

	return output