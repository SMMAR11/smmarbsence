# coding: utf-8

# Import
from django import forms

class ModifierCompte(forms.ModelForm) :
	
	class Meta :

		# Import
		from app.models import TUtilisateur

		fields = [
			'courr_second_util',
			'email',
			'email_auto_courr_princ',
			'email_auto_courr_second',
			'first_name',
			'last_name',
		]
		model = TUtilisateur
		labels = {
			'email' : 'Courriel principal',
			'last_name' : 'Nom de famille'
		}
		widgets = {
			'courr_second_util' : forms.TextInput(attrs = { 'input-group-addon' : 'email' }),
			'email' : forms.TextInput(attrs = { 'input-group-addon' : 'email' }),
			'email_auto_courr_princ' : forms.RadioSelect(choices = [(True, 'Oui'), (False, 'Non')]),
			'email_auto_courr_second' : forms.RadioSelect(choices = [(True, 'Oui'), (False, 'Non')])
		}

	def __init__(self, *args, **kwargs) :

		# Import
		from app.functions import init_mess_err

		super(ModifierCompte, self).__init__(*args, **kwargs)

		# Passage de certains champs à l'état requis
		self.fields['email'].required = True
		self.fields['first_name'].required = True
		self.fields['last_name'].required = True

		# Initialisation des messages d'erreur
		init_mess_err(self)