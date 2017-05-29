# coding: utf-8

# Import
from django import forms

class GererAgent(forms.ModelForm) :

	# Champs
	zs_password = forms.CharField(label = 'Mot de passe', widget = forms.PasswordInput())
	zs_password_bis = forms.CharField(label = 'Confirmation du mot de passe', widget = forms.PasswordInput())

	class Meta :

		# Import
		from app.models import TUtilisateur

		fields = [
			'courr_second_util',
			'email',
			'email_auto_courr_princ',
			'email_auto_courr_second',
			'en_act',
			'first_name',
			'gpe_util',
			'is_active',
			'last_name',
			'solde_cet_util',
			'type_util',
			'username'
		]
		model = TUtilisateur
		labels = {
			'email' : 'Courriel principal',
			'is_active' : 'Le compte doit-il être actif ?',
			'last_name' : 'Nom de famille'
		}
		widgets = {
			'courr_second_util' : forms.TextInput(attrs = { 'input-group-addon' : 'email' }),
			'email' : forms.TextInput(attrs = { 'input-group-addon' : 'email' }),
			'email_auto_courr_princ' : forms.RadioSelect(choices = [(True, 'Oui'), (False, 'Non')]),
			'email_auto_courr_second' : forms.RadioSelect(choices = [(True, 'Oui'), (False, 'Non')]),
			'en_act' : forms.RadioSelect(choices = [(True, 'Oui'), (False, 'Non')]),
			'gpe_util' : forms.SelectMultiple(attrs = { 'm2m' : 'on' }),
			'is_active' : forms.RadioSelect(choices = [(True, 'Oui'), (False, 'Non')]),
			'type_util' : forms.SelectMultiple(attrs = { 'm2m' : 'on' })
		}

	def __init__(self, *args, **kwargs) :

		# Import
		from app.functions import init_mess_err

		# Initialisation des arguments
		instance = kwargs.get('instance', None)
		self.kw_modif_mdp_agent = kwargs.pop('kw_modif_mdp_agent', False)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = { 'solde_cet_util' : instance.get_solde_cet_util__str() })

		super(GererAgent, self).__init__(*args, **kwargs)

		# Passage de certains champs à l'état requis
		self.fields['email'].required = True
		self.fields['first_name'].required = True
		self.fields['last_name'].required = True

		# Initialisation des messages d'erreur
		init_mess_err(self)

		if self.kw_modif_mdp_agent == False and self.instance.get_pk() :

			# Suppression des champs "mot de passe" si modification globale d'une instance
			del self.fields['zs_password']
			del self.fields['zs_password_bis']

		# Suppression des champs non-personnalisés si modification du mot de passe
		if self.kw_modif_mdp_agent == True :
			del self.fields['courr_second_util']
			del self.fields['email']
			del self.fields['email_auto_courr_princ']
			del self.fields['email_auto_courr_second']
			del self.fields['en_act']
			del self.fields['first_name']
			del self.fields['gpe_util']
			del self.fields['is_active']
			del self.fields['last_name']
			del self.fields['solde_cet_util']
			del self.fields['type_util']
			del self.fields['username']

	def clean(self) :

		# Import
		from django.conf import settings

		# Stockage des données du formulaire
		cleaned_data = super(GererAgent, self).clean()
		val_password = cleaned_data.get('zs_password')
		val_password_bis = cleaned_data.get('zs_password_bis')

		# Vérification du mot de passe
		if val_password :
			if 6 <= len(val_password) <= 20 :
				if val_password_bis and val_password != val_password_bis :
					self.add_error('__all__', 'Les mots de passe saisis ne correspondent pas.')
			else :
				self.add_error('zs_password', settings.ERROR_MESSAGES['invalid'])

	def save(self, commit = True) :

		# Imports
		from app.models import TGroupesUtilisateur
		from app.models import TRolesUtilisateur
		from datetime import date

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_password = cleaned_data.get('zs_password')
		val_gpe_util = cleaned_data.get('gpe_util')
		val_type_util = cleaned_data.get('type_util')

		# Création/modification d'une instance TUtilisateur
		obj = super(GererAgent, self).save(commit = False)
		if self.kw_modif_mdp_agent == True or not self.instance.get_pk() : obj.set_password(val_password)
		obj.save()

		if self.kw_modif_mdp_agent == False :

			# Liaison avec la table t_roles_utilisateur
			obj.get_role_util_set().all().delete()
			for tu in val_type_util : TRolesUtilisateur.objects.create(code_type_util = tu, id_util = obj)

			# Liaison avec la table t_groupes_utilisateur
			obj.get_gpe_util_set().all().delete()
			for gu in val_gpe_util : TGroupesUtilisateur.objects.create(id_gpe_util = gu, id_util = obj)

		return obj

class GererStatutAgent(forms.ModelForm) :

	# Champ
	zsc_pk = forms.IntegerField(label = '', required = False, widget = forms.HiddenInput(attrs = { 'readonly' : True }))

	class Meta :

		# Import
		from app.models import TStatutsUtilisateur

		fields = ['mois_deb_statut_util', 'num_annee', 'statut_util']
		model = TStatutsUtilisateur

	def __init__(self, *args, **kwargs) :

		# Import
		from app.functions import init_mess_err

		# Initialisation des arguments
		self.kw_util = kwargs.pop('kw_util', None)

		super(GererStatutAgent, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		if self.instance.get_pk() : self.fields['zsc_pk'].initial = self.instance.get_pk()

	def clean(self) :

		# Import
		from app.models import TStatutsUtilisateur

		# Stockage des données du formulaire
		cleaned_data = super(GererStatutAgent, self).clean()
		val_pk = cleaned_data.get('zsc_pk')
		val_mois_deb_statut_util = cleaned_data.get('mois_deb_statut_util')
		val_annee = cleaned_data.get('num_annee')

		# Renvoi d'une erreur en cas de "piratage"
		if val_pk and self.kw_util.get_statut_util_set().filter(pk = val_pk).count() == 0 :
			self.add_error(
				'__all__', 
				'''
				Attention, vous essayez de modifier le compte agent de {}.
				'''.format(TStatutsUtilisateur.objects.get(pk = val_pk).get_util().get_nom_complet())
			)

		# Renvoi d'une erreur si simultanéité des statuts agent
		if val_mois_deb_statut_util and val_annee :

			# Initialisation du jeu de données
			qs_statut_util = self.kw_util.get_statut_util_set().filter(
				mois_deb_statut_util = val_mois_deb_statut_util, num_annee = val_annee
			)
			if self.instance.get_pk() : qs_statut_util = qs_statut_util.exclude(pk = self.instance.get_pk())

			if qs_statut_util.count() > 0 :
				self.add_error(
					'__all__', 
					'Veuillez ne pas renseigner plus d\'une fois la même période de début d\'un statut agent.'
				)

	def save(self, commit = True) :

		# Création/modification d'une instance TStatutsUtilisateur
		obj = super(GererStatutAgent, self).save(commit = False)
		if not self.instance.get_pk() : obj.id_util = self.kw_util
		obj.save()

		# Mise à jour de la table t_decomptes_utilisateur
		obj.get_util().calc_proratas()

		return obj

class GererTransactionCetAgent(forms.ModelForm) :

	# Import
	from django.conf import settings

	# Champs
	zsc_pk = forms.IntegerField(label = '', required = False, widget = forms.HiddenInput(attrs = { 'readonly' : True }))
	zl_annee = forms.ChoiceField(choices = [settings.CF_EMPTY_VALUE], label = 'Année')

	class Meta :

		# Import
		from app.models import TTransactionsCetUtilisateur

		fields = ['nbre_conges_trans_cet_util', 'nbre_rtt_trans_cet_util']
		model = TTransactionsCetUtilisateur

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import init_mess_err
		from datetime import date

		# Initialisation des arguments
		instance = kwargs.get('instance', None)
		self.kw_util = kwargs.pop('kw_util', None)
		self.kw_util_connect = kwargs.pop('kw_util_connect', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'nbre_conges_trans_cet_util' : instance.get_nbre_conges_trans_cet_util__str(),
				'nbre_rtt_trans_cet_util' : instance.get_nbre_rtt_trans_cet_util__str()
			})

		super(GererTransactionCetAgent, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		# L'agent est-il secrétaire (et super-secrétaire) ?
		est_secr = True if self.kw_util_connect and 'S' in self.kw_util_connect.get_type_util__list() else False
		est_super_secr = True if est_secr == True and self.kw_util_connect.get_est_super_secr() == True else False

		# Initialisation des choix valides de la liste déroulante des années
		if est_super_secr == True :
			tab_annee = [(a.get_pk(), a) for a in self.kw_util.get_decompt_util().all()]
		else :
			et = None; ou = None
			for a in self.kw_util.get_decompt_util().all().reverse() :
				if date.today() > a.get_plage_conges_annee()[1] : et = a
				if date.today() > a.get_plage_rtt_annee()[1] : ou = a

			# Suppression des doublons + tri dans l'ordre décroissant
			tab_annee = sorted(
				list(set([(a.get_pk(), a) for a in [elem for elem in [et, ou] if elem is not None]])),
				key = lambda l : -l[0]
			)

		# Définition des années valides
		self.fields['zl_annee'].choices += tab_annee

		if self.instance.get_pk() :
			for cle, val in {
				'zsc_pk' : self.instance.get_pk(), 'zl_annee' : self.instance.get_annee().get_pk()
			}.items() : self.fields[cle].initial = val

	def clean(self) :

		# Imports
		from app.functions import get_local_format
		from app.models import TAnnee
		from app.models import TTransactionsCetUtilisateur
		from datetime import date
		from num2words import num2words
		import dateutil.relativedelta

		'''
		Initialisation d'un message d'erreur
		_nbre : Nombre de jours
		_gta : Congés payés ou RTT ?
		_a : Année
		Retourne une chaîne de caractères
		'''
		def init_mess(_nbre, _gta, _a) :
			if _nbre > 0 :
				if _nbre > 1 :
					mess = '''
					Seuls {0} jours de {1} n'ont pas encore été transférés sur votre compte épargne temps pour
					l'année {2}.
					'''.format(num2words(_nbre, lang = 'fr'), _gta[1], _a)
				else :
					mess = '''
					Seul un jour de {0} n'a pas encore été transféré sur votre compte épargne temps pour l'année {1}.
					'''.format(_gta[0], _a)
			else :
				mess = '''
				Vous avez déjà atteint la limite de transfert de {0} sur votre compte épargne temps pour l'année {1}.
				'''.format(_gta[1], _a)
			return mess

		# Stockage des données du formulaire
		cleaned_data = super(GererTransactionCetAgent, self).clean()
		val_pk = cleaned_data.get('zsc_pk')
		val_annee = cleaned_data.get('zl_annee')
		val_nbre_conges_trans_cet_util = cleaned_data.get('nbre_conges_trans_cet_util')
		val_nbre_rtt_trans_cet_util = cleaned_data.get('nbre_rtt_trans_cet_util')

		# Stockage d'instances globales
		obj_annee = TAnnee.objects.get(pk = val_annee) if val_annee else None

		# Renvoi d'une erreur en cas de "piratage"
		if val_pk and self.kw_util.get_trans_cet_util_set().filter(pk = val_pk).count() == 0 :
			self.add_error(
				'__all__', 
				'''
				Attention, vous essayez de modifier le compte épargne temps de {}.
				'''.format(TTransactionsCetUtilisateur.objects.get(pk = val_pk).get_util().get_nom_complet())
			)

		# L'agent est-il secrétaire (et super-secrétaire) ?
		est_secr = True if self.kw_util_connect and 'S' in self.kw_util_connect.get_type_util__list() else False
		est_super_secr = True if est_secr == True and self.kw_util_connect.get_est_super_secr() == True else False

		if obj_annee and est_super_secr == False :

			# Définition des bornes disponibles pour une transaction entrante
			tab_bornes = {
				'C' : [
					obj_annee.get_plage_conges_annee()[1] + dateutil.relativedelta.relativedelta(days = 1),
					obj_annee.get_plage_conges_annee()[1] + dateutil.relativedelta.relativedelta(years = 1),
				],
				'RTT' : [elem + dateutil.relativedelta.relativedelta(years = 1)
				for elem in obj_annee.get_plage_rtt_annee()]
			}

			# Détermination d'une erreur potentielle et des paramètres du message d'erreur
			incoher = False
			mess = '''
			Les transactions entrantes sur le CET pour un {0} de l'année {1} doivent être effectuées entre le {2} et
			le {3}.
			'''
			if val_nbre_conges_trans_cet_util and not tab_bornes['C'][0] <= date.today() <= tab_bornes['C'][1] :
				incoher = True
				tab_format = [
					'congé payé',
					obj_annee,
					get_local_format(tab_bornes['C'][0]),
					get_local_format(tab_bornes['C'][1])
				]
			if val_nbre_rtt_trans_cet_util and not tab_bornes['RTT'][0] <= date.today() <= tab_bornes['RTT'][1] :
				incoher = True
				tab_format = [
					'RTT',
					obj_annee,
					get_local_format(tab_bornes['RTT'][0]),
					get_local_format(tab_bornes['RTT'][1])
				]

			# Renvoi d'une erreur si incohérence temporelle
			if incoher == True : self.add_error('__all__', mess.format(*tab_format))

		if obj_annee :

			# Tentative d'obtention de l'instance en cours
			inst = self.instance if self.instance.get_pk() else None

			# Stockage du nombre de jours non-transférés sur le CET
			nbre_j_cp_non_transf = self.kw_util.get_nbre_j_non_transf(True, obj_annee.get_pk(), inst)
			nbre_j_rtt_non_transf = self.kw_util.get_nbre_j_non_transf(False, obj_annee.get_pk(), inst)

			# Renvoi d'une erreur si incohérence entre la valeur saisie et le nombre de jours encore transférables sur
			# le CET
			if val_nbre_conges_trans_cet_util and val_nbre_conges_trans_cet_util > nbre_j_cp_non_transf :
				self.add_error('__all__', init_mess(nbre_j_cp_non_transf, ['congé payé', 'congés payés'], obj_annee))
			if val_nbre_rtt_trans_cet_util and val_nbre_rtt_trans_cet_util > nbre_j_rtt_non_transf :
				self.add_error('__all__', init_mess(nbre_j_rtt_non_transf, ['RTT', 'RTT'], obj_annee))

	def save(self, commit = True) :

		# Imports
		from app.functions import get_tz
		from app.models import TAnnee

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_annee = cleaned_data.get('zl_annee')

		# Création/modification d'une instance TTransactionsCetUtilisateur
		obj = super(GererTransactionCetAgent, self).save(commit = False)
		if not self.instance.get_pk() : obj.dt_trans_cet_util = get_tz(); obj.id_util = self.kw_util
		obj.num_annee = TAnnee.objects.get(pk = val_annee)
		obj.save()

		return obj

class TrierTransactionsCetAgent(forms.Form) :

	# Import
	from django.conf import settings

	tab_hist_cet_agent = [(elem, '{} ans'.format(elem)) for elem in [5, 10, 20]]
	tab_hist_cet_agent.insert(0, settings.CF_EMPTY_VALUE)

	# Champs
	zl_mode_tri = forms.ChoiceField(
		choices = [('TN', 'Tri naturel'), ('TAC', 'Tri par année croissante'), ('TAD', 'Tri par année décroissante')],
		initial = 'TN',
		label = 'Mode de tri'
	)
	zl_hist_trans_cet_util = forms.ChoiceField(choices = tab_hist_cet_agent, label = 'Historique', required = False)

	def __init__(self, *args, **kwargs) :

		# Import
		from app.functions import init_mess_err

		# Initialisation des arguments
		self.kw_consult = kwargs.pop('kw_consult', False)
		self.kw_util = kwargs.pop('kw_util', None)

		super(TrierTransactionsCetAgent, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

	def init_dtab(self, _req, *args, **kwargs) :

		# Stockage et mise en forme des données du formulaire
		if _req.method == 'GET' :
			val_mode_tri = self.fields['zl_mode_tri'].initial
			val_hist_trans_cet_util = self.fields['zl_hist_trans_cet_util'].initial
		else :
			val_mode_tri = _req.POST.get('zl_mode_tri')
			val_hist_trans_cet_util = _req.POST.get('zl_hist_trans_cet_util')
		if val_hist_trans_cet_util : val_hist_trans_cet_util = int(val_hist_trans_cet_util)

		# Initialisation des données de la datatable
		tab = []
		for tr in self.kw_util.get_tabl_cet(val_mode_tri, val_hist_trans_cet_util) :
			td = [
				tr['annee'],
				tr['nbre_conges_trans_cet_util'] if 'nbre_conges_trans_cet_util' in tr else '-',
				tr['nbre_rtt_trans_cet_util'] if 'nbre_rtt_trans_cet_util' in tr else '-',
				tr['nbre_j_abs'] if 'nbre_j_abs' in tr else '-',
				tr['total'],
				tr['dt_abs'] if 'dt_abs' in tr else '-'
			]

			if self.kw_consult == False :
				td.append('''
					<span action="?action=initialiser-formulaire-modification-transaction-entrante-cet-agent&id={0}"
					class="icon-without-text modify-icon pull-right"
					onclick="trait_get(event, 'modif_trans_cet_util');" title="Modifier"></span>
					'''.format(tr['pk']) if 'pk' in tr else ''
				)
				td.append('''
					<span action="?action=supprimer-transaction-entrante-cet-agent-etape-1&id={0}"
					class="delete-icon icon-without-text pull-right"
					onclick="trait_get(event, 'suppr_trans_cet_util');" title="Supprimer"></span>
					'''.format(tr['pk']) if 'pk' in tr else ''
				)

			tab.append('<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(elem) for elem in td])))

		return '''
		<div class="custom-table" id="dtab_consult_cet_{0}">
			<table border="1" bordercolor="#DDD">
				<thead>
					<tr>
						<th rowspan="3">Année</th>
						<th colspan="3">Épargne</th>
						<th rowspan="3">Total</th>
						<th rowspan="3">Congés pris</th>
						{1}
					</tr>
					<tr>
						<th colspan="2">Entrées</th>
						<th rowspan="2">Sorties</th>
					</tr>
					<tr>
						<th>Congés payés</th>
						<th>RTT</th>
					</tr>
				</thead>
				<tbody>{2}</tbody>
			</table>
		</div>
		'''.format(
			'gest_agent' if self.kw_consult == False else 'gest_compte',
			'<th rowspan="3"></th><th rowspan="3"></th>' if self.kw_consult == False else '',
			''.join(tab)
		)

class FiltrerAgents(forms.Form) :

	# Import
	from django.conf import settings
	
	# Champ
	zl_type_util = forms.ChoiceField(
		choices = [settings.CF_EMPTY_VALUE, (True, 'En activité'), (False, 'En inactivité')],
		label = 'Afficher les agents',
		required = False
	)

	def __init__(self, *args, **kwargs) :

		# Import
		from app.functions import init_mess_err

		super(FiltrerAgents, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

	def init_dtab(self, _req, *args, **kwargs) :

		# Imports
		from app.functions import transform_bool
		from app.models import TUtilisateur
		from django.core.urlresolvers import reverse

		# Stockage des données du formulaire
		val_type_util = self.fields['zl_type_util'].initial if _req.method == 'GET' else _req.POST.get('zl_type_util')

		# Définition du jeu de données
		qs_util = TUtilisateur.objects.filter(en_act = val_type_util) if val_type_util else TUtilisateur.objects.all()

		# Initialisation des données de la datatable
		tab = [[
			u.get_username(),
			u.get_last_name(),
			u.get_first_name(),
			transform_bool(u.get_en_act()),
			transform_bool(u.get_is_active()),
			'<a href="{}" class="inform-icon pull-right" title="Consulter l\'agent"></a>'.format(
				reverse('consult_agent', args = [u.get_pk()])
			)
		] for u in qs_util.order_by('username')]

		return '''
		<div class="custom-table" id="dtab_chois_agent">
			<table border="1" bordercolor="#DDD">
				<thead>
					<tr>
						<th>Nom d'utilisateur</th>
						<th>Nom de famille</th>
						<th>Prénom</th>
						<th>L'agent est-il en activité ?</th>
						<th>Le compte est-il actif ?</th>
						<th></th>
					</tr>
				</thead>
				<tbody>{}</tbody>
			</table>
		</div>
		'''.format(''.join(['<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tr])) for tr in tab]))