# coding: utf-8

# Import
from django import forms

class FiltrerAbsences(forms.Form) :

	# Import
	from django.conf import settings
	
	# Champs
	zcc_util = forms.MultipleChoiceField(label = 'Utilisateurs|Nom complet|__zcc__', widget = forms.SelectMultiple())
	zl_type_abs = forms.ChoiceField(
		choices = [settings.CF_EMPTY_VALUE], label = 'Type de l\'absence', required = False
	)
	zl_annee = forms.ChoiceField(choices = [settings.CF_EMPTY_VALUE], label = 'Année', required = False)
	zd_dt_deb_abs = forms.DateField(
		input_formats = ['%d/%m/%Y'],
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'Du' })
	)
	zd_dt_fin_abs = forms.DateField(
		input_formats = ['%d/%m/%Y'],
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'au' })
	)
	zl_etat_abs = forms.ChoiceField(
		choices = [settings.CF_EMPTY_VALUE, (1, 'Autorisée'), (0, 'En attente'), (-1, 'Refusée')],
		label = 'État de l\'absence',
		required = False
	)
	rb_gby = forms.ChoiceField(
		choices = [('U', 'Utilisateurs'), ('TA', 'Types d\'absence')],
		initial = 'U',
		label = 'Regrouper par',
		required = False,
		widget = forms.RadioSelect()
	)
	zcc_ajout_select_exist = forms.BooleanField(
		label = 'Ajouter à la sélection existante', required = False, widget = forms.CheckboxInput()
	)

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import get_obj_dt
		from app.functions import init_mess_err
		from app.models import TAnnee
		from app.models import TGroupeTypeAbsence
		from app.models import TUtilisateur

		# Initialisation des arguments
		self.kw_gby = kwargs.pop('kw_gby')
		kw_util = kwargs.pop('kw_util')

		super(FiltrerAbsences, self).__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		# Initialisation des choix valides de la liste déroulante des utilisateurs
		if 'S' in kw_util.get_type_util__list() :
			tab_util = [(
				u.get_pk(), '|'.join([u.get_nom_complet(), '__zcc__'])
			) for u in TUtilisateur.objects.filter(en_act = True)]
		else :
			tab_util = [(kw_util.get_pk(), '|'.join([kw_util.get_nom_complet(), '__zcc__']))]

		# Initialisation des choix valides de la liste déroulante des types d'absence
		tab_type_abs = []
		for gta in TGroupeTypeAbsence.objects.all() :
			tab_type_abs.append([gta, [(ta.get_pk(), ta) for ta in gta.get_type_abs_set().all()]])

		# Définition des utilisateurs, des années et des types d'absence valides
		self.fields['zcc_util'].choices = tab_util
		self.fields['zl_annee'].choices += [(a.get_pk(), a) for a in TAnnee.objects.all()]
		self.fields['zl_type_abs'].choices += tab_type_abs

		if self.kw_gby == False : del self.fields['rb_gby']

	def init_dtab(self, _req, *args, **kwargs) :

		# Imports
		from app.functions import suppr_doubl
		from app.models import TAbsence
		from app.models import TTypeAbsence
		from app.models import TUtilisateur
		from django.core.urlresolvers import reverse
		import datetime

		# Initialisation des données de la datatable
		tab = []

		# Initialisation du tableau des absences (session)
		if _req.method == 'GET' : _req.session['filtr_abs'] = []

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_util = self.fields['zcc_util'].initial
			val_type_abs = self.fields['zl_type_abs'].initial
			val_annee = self.fields['zl_annee'].initial
			val_dt_deb_abs = self.fields['zd_dt_deb_abs'].initial
			val_dt_fin_abs = self.fields['zd_dt_fin_abs'].initial
			val_etat_abs = self.fields['zl_etat_abs'].initial
			val_gby = self.fields['rb_gby'].initial if 'rb_gby' in self.fields else None
			val_ajout_select_exist = self.fields['zcc_ajout_select_exist'].initial
		else :
			val_util = _req.POST.getlist('{}-zcc_util'.format(self.prefix))
			val_type_abs = _req.POST.get('{}-zl_type_abs'.format(self.prefix))
			val_annee = _req.POST.get('{}-zl_annee'.format(self.prefix))
			val_dt_deb_abs = _req.POST.get('{}-zd_dt_deb_abs'.format(self.prefix))
			val_dt_fin_abs = _req.POST.get('{}-zd_dt_fin_abs'.format(self.prefix))
			val_etat_abs = _req.POST.get('{}-zl_etat_abs'.format(self.prefix))
			val_gby = _req.POST.get('{}-rb_gby'.format(self.prefix))
			val_ajout_select_exist = _req.POST.get('{}-zcc_ajout_select_exist'.format(self.prefix))

		# Définition des conditions "directes" de la requête
		tab_filter_dir = {}
		if val_annee : tab_filter_dir['num_annee'] = val_annee
		if val_dt_deb_abs : tab_filter_dir['dt_abs__0__gte'] = datetime.datetime.strptime(val_dt_deb_abs, '%d/%m/%Y')
		if val_dt_fin_abs : tab_filter_dir['dt_abs__0__lte'] = datetime.datetime.strptime(val_dt_fin_abs, '%d/%m/%Y')

		# Initialisation des conditions "indirectes" de la requête
		tab_filter_indir = { 'etat_abs' : [], 'type_abs' : [] }

		# Initialisation du jeu de données des utilisateurs
		qs_util = TUtilisateur.objects.filter(pk__in = val_util) if val_util else TUtilisateur.objects.none()

		for u in qs_util :
			for a in u.get_abs_set().filter(**tab_filter_dir) :

				# Préparation de la condition "indirecte" liée au type d'absence
				if val_type_abs :
					if a.get_type_abs_final().get_pk() == int(val_type_abs) :
						tab_filter_indir['type_abs'].append(a.get_pk())
				else :
					tab_filter_indir['type_abs'].append(a.get_pk())

				# Préparation de la condition "indirecte" liée à l'état d'absence
				if val_etat_abs :
					if a.get_etat_abs() == int(val_etat_abs) : tab_filter_indir['etat_abs'].append(a.get_pk())
				else :
					tab_filter_indir['etat_abs'].append(a.get_pk())

		# Préparation des absences (empilement si élément en commun dans tous les tableaux de conditions "indirectes")
		tab_pk = []
		for elem in tab_filter_indir['etat_abs'] :
			valide = True
			for elem_2 in tab_filter_indir.values() :
				if elem not in elem_2 : valide = False
			if valide == True : tab_pk.append(elem)

		# Réinitialisation du tableau des absences si besoin (session)
		if not val_ajout_select_exist : _req.session['filtr_abs'] = []

		# Préparation du tableau des absences (session)
		if self.kw_gby == False :
			for a in tab_pk :
				obj_abs = TAbsence.objects.get(pk = a)
				_req.session['filtr_abs'].append([
					obj_abs.get_pk(),
					obj_abs.get_util_emett().get_nom_complet(),
					str(obj_abs.get_type_abs_final()),
					obj_abs.get_dt_abs__fr_str(),
					str(obj_abs.get_annee()),
					obj_abs.get_etat_abs(True),
					'<a href="{}" class="inform-icon pull-right" title="Consulter l\'absence"></a>'.format(
						reverse('consult_abs', args = [obj_abs.get_pk()])
					)
				])
		else :
			if len(tab_pk) > 0 :

				# Initialisation du tableau des absences
				tab_abs = [TAbsence.objects.get(pk = elem) for elem in tab_pk]

				# Initialisation de tableaux
				tab_donn = []
				tab_etat_abs = { '' : 'Tous', '-1' : 'Refusée', '0' : 'En attente', '1' : 'Autorisée' }

				if val_gby == 'U' :

					# Groupement d'objets par utilisateur
					tab_abs__group_by = [[j for j in tab_abs if j.get_util_emett() == i] for i in set(
						map(lambda l : l.get_util_emett(), tab_abs)
					)]

					for elem in tab_abs__group_by :

						# Calcul du nombre de jours d'absence
						nbre_dt_abs = 0
						for a in elem : nbre_dt_abs += a.get_nbre_dt_abs()

						tab_donn.append([
							elem[0].get_util_emett().get_nom_complet(),
							str(TTypeAbsence.objects.get(pk = val_type_abs)) if val_type_abs else 'Tous',
							val_annee or 'Toutes',
							tab_etat_abs[val_etat_abs],
							len(elem),
							'{0:g}'.format(nbre_dt_abs)
						])

					# Envoi des données triées par nom complet croissant
					for elem in sorted(tab_donn, key = lambda l : l[0]) : _req.session['filtr_abs'].append(elem)

				else :

					# Groupement d'objets par type d'absence
					tab_abs__group_by = [[j for j in tab_abs if j.get_type_abs_final() == i] for i in set(
						map(lambda l : l.get_type_abs_final(), tab_abs)
					)]

					for elem in tab_abs__group_by :

						# Initialisation de variables
						tab_util = []
						nbre_dt_abs = 0

						for a in elem :

							# Empilement des utilisateurs concernés par la ligne
							if a.get_util_emett().get_nom_complet() not in tab_util :
								tab_util.append(a.get_util_emett().get_nom_complet())

							# Calcul du nombre de jours d'absence
							nbre_dt_abs += a.get_nbre_dt_abs()

						tab_donn.append([
							', '.join(sorted(tab_util)),
							str(elem[0].get_type_abs_final()),
							val_annee or 'Toutes',
							tab_etat_abs[val_etat_abs],
							len(elem),
							'{0:g}'.format(nbre_dt_abs)
						])

					# Envoi des données triées par type d'absence croissant
					for elem in sorted(tab_donn, key = lambda l : l[1]) : _req.session['filtr_abs'].append(elem)

		# Suppression des doublons
		_req.session['filtr_abs'] = suppr_doubl(_req.session['filtr_abs'])

		# Empilement des lignes de la datatable
		if self.kw_gby == False :
			for elem in _req.session['filtr_abs'] : tab.append(elem[1:])
		else :
			for elem in _req.session['filtr_abs'] : tab.append(elem)

		if self.kw_gby == False :
			output = '''
			<div class="custom-table" id="dtab_select_abs">
				<table border="1" bordercolor="#DDD">
					<thead>
						<tr>
							<th>Nom complet de l'agent</th>
							<th>Type de l'absence</th>
							<th>Date de l'absence</th>
							<th>Année de l'absence</th>
							<th>État de l'absence</th>
							<th></th>
						</tr>
					</thead>
					<tbody>{}</tbody>
				</table>
			</div>
			'''
		else :
			output = '''
			<div class="custom-table" id="dtab_regroup_abs">
				<table border="1" bordercolor="#DDD">
					<thead>
						<tr>
							<th>Nom complet de l'agent/des agents</th>
							<th>Type de l'absence</th>
							<th>Année de l'absence</th>
							<th>État de l'absence</th>
							<th>Nombre d'absences</th>
							<th>Nombre de jours d'absence</th>
						</tr>
					</thead>
					<tbody>{}</tbody>
				</table>
			</div>
			'''
			
		return output.format(''.join(['<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tr])) for tr in tab]))