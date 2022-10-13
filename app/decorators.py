# coding: utf-8

'''
Vérification de l'accès à une page
_mod : Clé du module
_elem : Clé de l'élément du module
'''
def verif_acces(_mod = None, _elem = None) :
	def _method_wrapper(_vf) :
		def _args_wrapper(_req, *args, **kwargs) :

			# Imports
			from app.functions import get_menu
			from django.core.exceptions import PermissionDenied

			# Jaugeage de l'éventualité d'une erreur 403
			tab = get_menu(_req)
			erreur_403 = False
			if not _req.user.is_authenticated :
				erreur_403 = True
			else :
				if _mod :
					if _mod in tab :
						if _elem and _elem not in tab[_mod]['mod_items'] : erreur_403 = True
					else :
						erreur_403 = True

			# Exécution de la vue ou erreur 403
			if erreur_403 == False :
				return _vf(_req, *args, **kwargs)
			else :
				raise PermissionDenied

		return _args_wrapper
	return _method_wrapper