# coding: utf-8

'''
Validation d'une chaîne de caractères
_val : Chaîne de caractères
Retourne la chaîne de caractères sauf si erreur
'''
def valid_cdc(_val) :

	# Import
	from django.core.exceptions import ValidationError

	# Initialisation des caractères interdits
	tab = [';', '"', '|']

	# Renvoi d'une erreur si un ou plusieurs caractères interdits
	trouve = []
	for i in range(len(_val)) :
		for elem in tab :
			if _val[i] == elem : trouve.append(elem)
	if len(trouve) > 0 : raise ValidationError('Le caractère « {} » est interdit.'.format(trouve[0]))

	return _val

'''
Validation d'un nombre à une décimale se terminant par 0 ou 5
_val : Nombre à une décimale
Retourne le nombre à une décimale sauf si erreur
'''
def valid_float(_val) :

	# Imports
	from django.conf import settings
	from django.core.exceptions import ValidationError
	import numbers

	erreur = False

	if isinstance(_val, numbers.Number) == True :

		# Conversion float -> float -> string
		val__str = str(float(_val))

		# Calcul du nombre de décimales
		nbre_decim = val__str[::-1].find('.')

		# Vérification de la décimale
		if nbre_decim > 1 :
			erreur = True
		else :
			if val__str[-1] not in ['0', '5'] : erreur = True

	else :
		erreur = True

	# Renvoi d'une erreur si la valeur saisie est incohérente
	if erreur : raise ValidationError(settings.ERROR_MESSAGES['invalid'])

	return _val

'''
Validation de l'upload d'un fichier au format PDF
_val : Fichier uploadé
Retourne le fichier uploadé sauf si erreur
'''
def valid_pdf(_val) :

	# Imports
	import os
	from django.core.exceptions import ValidationError

	if os.path.splitext(_val.name)[1] != '.pdf' :

		# Renvoi d'une erreur si le fichier n'est pas au format PDF
		raise ValidationError('Veuillez renseigner un fichier au format PDF.')

	else :

		# Renvoi d'une erreur si la taille du fichier est supérieure à 20 Mo
		taille = 20
		if _val.size > taille * 1048576 :
			raise ValidationError(
				'Veuillez renseigner un fichier dont la taille est inférieure ou égale à {} Mo.'.format(taille)
			)

	return _val