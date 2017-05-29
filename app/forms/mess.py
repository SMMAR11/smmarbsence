# coding: utf-8

# Import
from django import forms

class SelectionnerMessages(forms.Form) :
	
	# Champ
	zcc_mess_util = forms.MultipleChoiceField(label = '|__zcc__|Lu|De|Objet|Reçu le|', widget = forms.SelectMultiple())

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import init_mess_err
		from django.core.urlresolvers import reverse

		# Initialisation des arguments
		kw_util = kwargs.pop('kw_util', None)
		kw_est_arch = kwargs.pop('kw_est_arch', False)

		super(SelectionnerMessages, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self, False)

		# Préparation du tableau des messages
		tab_mess_util = []
		if kw_util :
			for mu in kw_util.get_qs_mess_util_set(kw_est_arch) :
				tab_mess_util.append([
					mu.get_pk(),
					'|'.join([
						'__zcc__',
						'<span class="{}"></span>'.format(
							'fa fa-check-circle-o' if mu.get_est_lu() == True else 'fa fa-circle-o'
						),
						mu.get_mess().get_emett_mess(),
						mu.get_mess().get_obj_mess(),
						mu.get_mess().get_dt_mess__str(),
						'''
						<a href="{}" class="inform-icon pull-right" title="Consulter le message"></a>
						'''.format(reverse('consult_mess', args = [mu.get_pk()]))
					])
				])

		# Préparation des choix de chaque champ personnalisé
		self.fields['zcc_mess_util'].choices = tab_mess_util