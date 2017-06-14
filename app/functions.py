# coding: utf-8

'''
Affichage d'une demande de suppression
_act : URL traitant la demande de suppression
_suff : Suffixe d'une fenêtre modale
Retourne une chaîne de caractères
'''
def affich_dem_suppr(_act, _suff) :
	return '''
	<div class="row">
		<div class="col-xs-6">
			<button action="{0}" class="center-block custom-btn green-btn" onclick="trait_get(event, '{1}');">
				Oui
			</button>
		</div>
		<div class="col-xs-6">
			<button class="center-block custom-btn green-btn" data-dismiss="modal">Non</button>
		</div>
	</div>
	'''.format(_act, _suff)

'''
Calcul du nombre de jours d'absence
_tab : Tableau de données de l'absence
Return un nombre entier ou à une décimale
'''
def calcul_nbre_j(_tab) :

	# Import
	from app.functions import init_tranche_dt_abs

	output = 0
	for elem in init_tranche_dt_abs(_tab) :
		if elem['indisp_dt_abs'] == 'WD' :
			output += 1
		else :
			output += 0.5

	return output

'''
Envoi d'un message à un groupe d'utilisateurs
_req : Objet "requête"
_tab_donn : Données du message
_tab_util : Utilisateurs concernés
'''
def envoy_mess(_req, _tab_donn, _tab_util) :

	# Imports
	from app.apps import AppConfig
	from app.functions import get_tz
	from app.models import TMessage
	from app.models import TMessagesUtilisateur
	from bs4 import BeautifulSoup
	from django.conf import settings
	from django.core.mail import send_mail

	# Finition des données du message (ajout de la date d'envoi/de réception)
	_tab_donn['dt_mess'] = get_tz()

	# Création d'une instance TMessage
	obj_mess = TMessage.objects.create(**_tab_donn)

	# Initialisation des courriels susceptibles de recevoir un email
	tab_to = []

	for u in _tab_util :

		# Création d'une instance TMessagesUtilisateur
		TMessagesUtilisateur.objects.create(id_mess = obj_mess, id_util = u)

		# Empilement des courriels susceptibles de recevoir un email
		if u.get_email_auto_courr_princ() == True : tab_to.append(u.get_email())
		if u.get_courr_second_util() and u.get_email_auto_courr_second() == True :
			tab_to.append(u.get_courr_second_util())

	# Envoi d'un email groupé ou non
	if settings.CAN_SEND_EMAILS == True and len(tab_to) > 0 :

		# Suppression de l'ancre HTML (attention, la valeur de l'attribut href et le contenu de la balise doivent être
		# similaires)
		set_corps_mess = BeautifulSoup(obj_mess.get_corps_mess(), 'html.parser')
		for elem in set_corps_mess.find_all('a') : elem.replaceWith(_req.build_absolute_uri(elem['href']))

		# Envoi de l'email
		send_mail(
			'[{0}] {1}'.format(AppConfig.verbose_name, obj_mess.get_obj_mess()),
			str(set_corps_mess),
			'TODO',
			sorted(list(set(tab_to))),
			fail_silently = False
		)

'''
Détermination de l'ouvrabilité selon une date
_dt : Objet "date"
Retourne un booléen
'''
def est_ouvr(_dt) :

	# Imports
	from app.models import TDateFermeture
	from workalendar.europe import France

	output = False

	# Initialisation d'un calendrier français
	cal = France()

	# Vérification de l'ouvrabilité
	if cal.is_working_day(_dt) == True and TDateFermeture.objects.filter(pk = _dt).count() == 0 : output = True

	return output

'''
Génération d'une chaîne de caractères selon le datetime courant
Retourne une chaîne de caractères
'''
def gener_cdc() :
	import hashlib; import time; return hashlib.sha1(time.strftime('%d%m%Y%H%M%S').encode()).hexdigest()

'''
Mise en forme d'un objet "datetime", "date" ou "time" au format local
_obj : Objet
Retourne un objet "datetime", "date" ou "time"
'''
def get_local_format(_obj) :

	# Imports
	from django.conf import settings
	from django.utils.formats import date_format
	from django.utils.formats import time_format
	import datetime

	output = _obj
	if _obj and settings.USE_L10N == True :
		if isinstance(_obj, datetime.datetime) :
			output = date_format(_obj, 'd/m/Y H:i:s')
		elif isinstance(_obj, datetime.date) :
			output = date_format(_obj, 'd/m/Y')
		elif isinstance(_obj, datetime.time) :
			output = time_format(_obj, 'H:M:S')	

	return output
	
'''
Obtention d'objets "date"
_code : Code d'un objet "date"
_abrev : Abréviation ou pas ?
Retourne un tableau
'''
def get_obj_dt(_code, _abrev = False) :

	# Import
	from app.models import TAnnee

	output = None

	# Obtention des mois au format français
	if _code == 'MONTHS' and _abrev == False :
		output = [
			'Janvier',
			'Février',
			'Mars',
			'Avril',
			'Mai',
			'Juin',
			'Juillet',
			'Août',
			'Septembre',
			'Octobre',
			'Novembre',
			'Décembre'
		]

	# Obtention des jours de la semaine au format français
	if _code == 'WEEKDAYS' :
		if _abrev == False :
			output = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
		else :
			output = ['Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa', 'Di']

	# Obtention d'une tranche d'années
	if _code == 'YEARS' : output = [elem.get_pk() for elem in TAnnee.objects.all()]

	return output

'''
Obtention du menu complet de l'application
_req : Objet "requête"
Retourne un tableau associatif
'''
def get_menu(_req) :

	# Imports
	from app.models import TUtilisateur
	from django.conf import settings
	from django.core.urlresolvers import reverse

	output = {
		'cal_abs' : {
			'mod_href' : reverse('cal_abs'),
			'mod_img' : settings.STATIC_URL + 'images/thumbnails/cal_abs/main.png',
			'mod_items' : {},
			'mod_name' : 'Calendrier des absences',
			'mod_rank' : 4,
			'mod_rights' : ['A', 'D', 'S']
		},
		'gest_abs' : {
			'mod_href' : reverse('gest_abs'),
			'mod_img' : settings.STATIC_URL + 'images/thumbnails/gest_abs/main.png',
			'mod_items' : {
				'ajout_abs' : {
					'item_href' : reverse('ajout_abs'),
					'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_abs/add.png',
					'item_name' : 'Ajouter une absence'
				},
				'chois_abs' : {
					'item_href' : reverse('chois_abs'),
					'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_abs/consult.png',
					'item_name' : 'Consulter une absence'
				},
				'verif_abs' : {
					'item_banned_for' : [['A']],
					'item_href' : reverse('chois_verif_abs'),
					'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_abs/verify.png',
					'item_name' : 'Vérifier une absence'
				}
			},
			'mod_name' : 'Gestion des absences',
			'mod_rank' : 3,
			'mod_rights' : ['A', 'D', 'S']
		},
		'gest_agents' : {
			'mod_href' : reverse('gest_agents'),
			'mod_img' : settings.STATIC_URL + 'images/thumbnails/gest_agents/main.png',
			'mod_items' : {
				'ajout_agent' : {	
					'item_href' : reverse('ajout_agent'),
					'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_agents/add.png',
					'item_name' : 'Ajouter un agent'
				},
				'chois_agent' : {
					'item_href' : reverse('chois_agent'),
					'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_agents/consult.png',
					'item_name' : 'Consulter un agent'
				}
			},
			'mod_name' : 'Gestion des agents',
			'mod_rank' : 2,
			'mod_rights' : ['S']
		},
		'gest_compte' : {
			'mod_href' : reverse('consult_compte'),
			'mod_img' : settings.STATIC_URL + 'images/thumbnails/gest_compte/main.png',
			'mod_items' : {},
			'mod_name' : 'Consultation du compte',
			'mod_rank' : 1,
			'mod_rights' : ['A', 'D', 'S']
		},
		'real_etats' : {
			'mod_href' : reverse('real_etats'),
			'mod_img' : settings.STATIC_URL + 'images/thumbnails/real_etats/main.png',
			'mod_items' : {
				'select_abs' : {	
					'item_href' : reverse('select_abs'),
					'item_img' : settings.STATIC_URL + 'images/thumbnails/real_etats/main.png',
					'item_name' : 'En sélectionnant des absences'
				},
				'regroup_abs' : {	
					'item_href' : reverse('regroup_abs'),
					'item_img' : settings.STATIC_URL + 'images/thumbnails/real_etats/main.png',
					'item_name' : 'En regroupant des absences'
				}
			},
			'mod_name' : 'Réalisation d\'états',
			'mod_rank' : 5,
			'mod_rights' : ['A', 'D', 'S']
		}
	}

	# Initialisation du menu utilisateur
	tab_menu_util = {}
	if _req.user.is_authenticated() :

		# Obtention d'une instance TUtilisateur
		obj_util = TUtilisateur.objects.get(pk = _req.user)

		# Désignation des modules et des éléments accessibles par l'utilisateur selon ses rôles et son type de compte
		for cle_mod, val_mod in output.items() :

			# Vérification de l'accessibilité du module
			mod_access = False
			for tu in obj_util.get_type_util__list() :
				if tu in val_mod['mod_rights'] : mod_access = True

			if mod_access == True :

				# Déclaration du tableau des éléments du module
				tab_elem_mod = {}

				for cle_elem, val_elem in val_mod['mod_items'].items() :

					# Vérification de l'accessibilité de l'élément
					elem_access = True
					if 'item_banned_for' in val_elem :
						for elem in val_elem['item_banned_for'] :
							if elem == obj_util.get_type_util__list() : elem_access = False

					# Empilement du tableau des éléments du module
					if elem_access == True : tab_elem_mod[cle_elem] = val_elem

				# Mise à jour des éléments du module
				val_mod['mod_items'] = tab_elem_mod

				tab_menu_util[cle_mod] = val_mod

		# Surchargement de la valeur de sortie
		output = tab_menu_util

	# Tri du tableau par ordre d'affichage et conversion en tableau associatif
	def get_mod_rank(_val) : return _val[1]['mod_rank']
	output = dict(sorted(output.items(), key = get_mod_rank))

	return output

def get_tz() : from django.utils import timezone; return timezone.now()

'''
Obtention d'un gabarit normé pour chaque attribut disponible en consultation
_tab : Tableau d'attributs
Retourne un tableau associatif
'''
def init_consult(_tab) :

	# Import
	from django.template.defaultfilters import safe

	output = {}

	for cle, val in _tab.items() :
		if 'label' in val and 'value' in val :

			# Stockage du label et de la valeur attributaire
			get_label = val['label']
			get_value = val['value'] if val['value'] else val['null'] if 'null' in val else ''

			# Mise en forme d'un attribut
			attr = ''
			if 'datatable' in val :
				if val['datatable'] == True and 'datatable_header' in val :
					attr = '''
					<span class="attribute-label">{0}</span>
					<div class="custom-table" id="dtab_{1}">
						<table border="1" bordercolor="#DDD">
							<thead>
								<tr>{2}</tr>
							</thead>
							<tbody>{3}</tbody>
						</table>
					</div>
					'''.format(
						get_label,
						cle,
						''.join(['<th>{}</th>'.format(elem) for elem in val['datatable_header'].split('|')]),
						''.join(['<tr>{}</tr>'.format(
							''.join(['<td>{}</td>'.format(td) for td in tr])
						) for tr in get_value])
					)
			elif 'pdf' in val :
				if val['pdf'] == True and len(get_value) > 0 :
					attr = '''
					<a href="{0}" target="blank" class="icon-with-text pdf-icon">{1}</a>
					'''.format(get_value, get_label)
			else :
				attr = '''
				<span class="attribute-label">{0}</span>
				<div class="attribute">{1}</div>
				'''.format(get_label, get_value)

			# Mise en forme du gabarit
			if 'last_child' in val :
				if val['last_child'] == True :
					gab = '<div class="attribute-wrapper" style="margin-bottom: 0;">{}</div>'.format(attr)
				else :
					gab = None
			else :
				gab = '<div class="attribute-wrapper">{}</div>'.format(attr)

		# Tentative d'empilage du tableau associatif de sortie
		if gab :
			output[cle] = safe(gab)
		else :
			raise ValueError('Aucun gabarit n\'est disponible pour l\'attribut « {} ».'.format(cle))

	return output

'''
Obtention d'une fenêtre modale
_suff : Suffixe
_entete : En-tête
_corps : Contenu
Retourne une chaîne de caractères
'''
def init_fm(_suff, _entete, _corps = '') :

	# Import
	from django.template.defaultfilters import safe

	fm = '''
	<div class="custom-modal fade modal" data-backdrop="static" data-keyboard="false" id="fm_{suffix}" role="dialog" 
	tabindex="-1">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button class="close" data-dismiss="modal" type="button">&times;</button>
					<span class="modal-title">{header}</span>
				</div>
				<div class="modal-body">
					<span id="za_fm_{suffix}" class="form-root">{body}</span>
					<div class="modal-padding-bottom"></div>
				</div>
			</div>
		</div>
	</div>
	'''.format(suffix = _suff, header = _entete, body = _corps)

	return safe(fm)
	
'''
Obtention d'un gabarit normé pour chaque champ d'un formulaire
_form : Objet "formulaire"
_pref : Préfixe utilisé sur chaque champ d'un formulaire
Retourne un tableau associatif
'''
def init_form(_form) :

	# Imports
	from bs4 import BeautifulSoup
	from django.template.defaultfilters import safe

	output = {}

	# Mise en forme du gabarit par défaut
	gab_defaut = '''
	<div class="field-wrapper" id="fw_{0}">
		<span class="field-label">{1}</span>
		<span class="field">{2}</span>
		<span class="field-error-message"></span>
	</div>
	'''

	for champ in _form :
		gab = None

		# Conversion du champ en code HTML
		champ_html = '{}'.format(champ)

		# Définition du nom du champ (valeur de l'attribut "name")
		if _form.prefix :
			set_name = '{0}-{1}'.format(_form.prefix, champ.name)
		else :
			set_name = champ.name

		# Stockage du type de champ
		balise_init = BeautifulSoup(champ_html, 'html.parser').find_all()[0].name

		if balise_init == 'a' :

			bs = BeautifulSoup(champ_html, 'html.parser')

			# Obtention de chaque balise <input/> du champ
			tab_input = bs.find_all('input')

			# Définition de la balise <span/> relatif au fichier
			if len(tab_input) > 1 :
				span = '''
				<span class="delete-file">
					{0}
					<label for="{1}-clear_id">Effacer</label>
				</span>
				'''.format(tab_input[0], set_name)
			else :
				span = ''

			gab = '''
			<div class="field-wrapper" id="fw_{0}">
				<span class="field-label">{1}</span>
				<div class="if-container">
					<span class="field">{2}</span>
					<span class="if-trigger">Parcourir</span>
					<div class="if-return">
						<span class="file-infos">
							{3}
						</span>
						{4}
					</div>
				</div>
				<span class="field-error-message"></span>
			</div>
			'''.format(
				set_name, 
				champ.label, 
				tab_input[-1],
				bs.find_all('a')[0]['href'], 
				span
			)
		
		if balise_init == 'input' :

			# Mise en forme d'une zone de saisie de type "checkbox"
			if 'type="checkbox"' in champ_html :
				gab = '''
				<div class="field-wrapper" id="fw_{0}">
					<span class="field">{1}</span>
					<span class="field-label">{2}</span>
					<span class="field-error-message"></span>
				</div>
				'''.format(set_name, champ, champ.label)

			# Mise en forme d'une zone de saisie de type "file"
			if 'type="file"' in champ_html :
				gab = '''
				<div class="field-wrapper" id="fw_{0}">
					<span class="field-label">{1}</span>
					<div class="if-container">
						<span class="field">{2}</span>
						<span class="if-trigger">Parcourir</span>
					</div>
					<span class="field-error-message"></span>
				</div>
				'''.format(set_name, champ.label, champ)

			# Mise en forme d'une zone de saisie de type "hidden"
			if 'type="hidden"' in champ_html :
				gab = '''
				<div class="field-wrapper" id="fw_{0}" style="margin-bottom: 0;">
					<span class="field-label">{1}</span>
					<span class="field">{2}</span>
					<span class="field-error-message"></span>
				</div>
				'''.format(set_name, champ.label, champ)

			# Mise en forme d'une zone de saisie de type "number"
			if 'type="number"' in champ_html :
				champ_html_modif = champ_html.replace('type="number"', 'type="text"')
				champ_html_modif = champ_html_modif.replace('step="any"', '')
				gab = gab_defaut.format(set_name, champ.label, champ_html_modif)

			# Mise en forme d'une zone de saisie de type "password"
			if 'type="password"' in champ_html :
				gab = gab_defaut.format(set_name, champ.label, champ)

			# Mise en forme d'une zone de saisie de type "text"
			if 'type="text"' in champ_html :
				if 'input-group-addon="date"' in champ_html :
					gab = '''
					<div class="field-wrapper" id="fw_{0}">
						<span class="field-label">{1}</span>
						<div class="form-group">
							<span class="field">
								<div class="input-group">
									{2}
									<span class="date input-group-addon">
										<input name="{3}__datepicker" type="hidden">
										<span class="glyphicon glyphicon-calendar"></span>
									</span>
								</div>
							</span>
						</div>
						<span class="field-error-message"></span>
					</div>
					'''.format(set_name, champ.label, champ, set_name)
				elif 'input-group-addon="email"' in champ_html :
					gab = '''
					<div class="field-wrapper" id="fw_{0}">
						<span class="field-label">{1}</span>
						<div class="form-group">
							<span class="field">
								<div class="input-group">
									{2}
									<span class="input-group-addon">
										<span class="fa fa-at"></span>
									</span>
								</div>
							</span>
						</div>
						<span class="field-error-message"></span>
					</div>
					'''.format(set_name, champ.label, champ, set_name)
				else :
					gab = gab_defaut.format(set_name, champ.label, champ)

		# Mise en forme d'une zone de liste
		if balise_init == 'select' :
			if 'multiple="multiple"' in champ_html :
				if 'm2m="on"' in champ_html :

					# Initialisation des colonnes de la balise <thead/>
					tab_elem = [
						champ.label.split('|')[1],
						'<input type="checkbox" id="id_{}__all" value="__all__">'.format(set_name)
					]
					tab_thead = ['<th>{}</th>'.format(elem) for elem in tab_elem]

					# Initialisation des lignes de la balise <tbody/>
					bs = BeautifulSoup(champ_html, 'html.parser')
					tab_tbody = []
					for index, elem in enumerate(bs.find_all('option')) :
						tab_elem = [
							elem.text, '<input type="checkbox" id="id_{0}_{1}" name="{2}" value="{3}" {4}>'.format(
								set_name,
								index,
								set_name,
								elem['value'],
								'checked' if elem.has_attr('selected') else ''
							)
						]
						tab_tbody.append('<tr>{}</tr>'.format(''.join(
							['<td>{}</td>'.format(elem) for elem in tab_elem]
						)))

				else :

					# Initialisation des colonnes de la balise <thead/>
					tab_thead = []
					for elem in champ.label.split('|')[1:] :
						if elem == '__zcc__' :
							elem = '<input type="checkbox" id="id_{}__all" value="__all__">'.format(set_name)
						tab_thead.append('<th>{}</th>'.format(elem))

					# Initialisation des lignes de la balise <tbody/>
					bs = BeautifulSoup(champ_html, 'html.parser')
					tab_tbody = []
					for index, elem in enumerate(bs.find_all('option')) :
						tab_td = []
						for elem_2 in elem.text.split('|') :
							if elem_2 == '__zcc__' :
								elem_2 = '<input type="checkbox" id="id_{0}_{1}" name="{2}" value="{3}" {4}>'.format(
									set_name,
									index,
									set_name,
									elem['value'],
									'checked' if elem.has_attr('selected') else ''
								)
							tab_td.append('<td>{}</td>'.format(elem_2))
						tab_tbody.append('<tr>{}</tr>'.format(''.join(tab_td)))

				gab = '''
				<div class="field-wrapper" id="fw_{0}">
					<span class="field-label">{1}</span>
					<div class="custom-table" id="dtab_{2}">
						<table border="1" bordercolor="#DDD" id="id_{3}">
							<thead><tr>{4}</tr></thead>
							<tbody>{5}</tbody>
						</table>
					</div>
					<span class="field-error-message"></span>
				</div>
				'''.format(
					set_name,
					champ.label.split('|')[0],
					set_name,
					set_name,
					''.join(tab_thead),
					''.join(tab_tbody)
				)
			else :
				gab = gab_defaut.format(set_name, champ.label, champ)

		# Mise en forme d'une zone de texte
		if balise_init == 'textarea' :
			gab = gab_defaut.format(set_name, champ.label, champ)

		# Mise en forme d'une zone de boutons radio
		if balise_init == 'ul' :
			gab = gab_defaut.format(set_name, champ.label, champ)

		# Tentative d'empilage du tableau associatif de sortie
		if gab :
			output[champ.name] = safe(gab)
		else :
			raise ValueError('Aucun gabarit n\'est disponible pour le champ « {} ».'.format(set_name))
		
	return output

'''
Initialisation d'un menu à vignettes
_tab : Tableau de vignettes
_lim : Limite par ligne
Retourne une chaîne de caractères
'''
def init_menu_vign(_tab, _lim) :

	# Import
	from django.template.defaultfilters import safe

	'''
	Initialisation d'une ligne de vignettes
	_prem : Indice du tableau _tab (première vignette de la future ligne)
	_nbre : Nombre de vignettes
	Retourne un tableau
	'''
	def init_lg(_prem, _nbre) :
		return ['<div class="col-sm-{0}">{1}</div>'.format(int(12 / _nbre), _tab[_prem + i]) for i in range(0, _nbre)]

	# Stockage du nombre de vignettes
	long_tab = len(_tab)

	# Stockage du nombre de lignes complètes
	nb_lg = int(long_tab / _lim)

	# Initialisation des lignes (complètes et incomplète)
	tab_lg = []
	for i in range(0, nb_lg) : tab_lg.append('<div class="row">{}</div>'.format(''.join(init_lg(i * _lim, _lim))))
	nb_vign_rest = long_tab % _lim
	if nb_vign_rest > 0 :
		tab_lg.append('<div class="row">{}</div>'.format(''.join(init_lg(nb_lg * _lim, nb_vign_rest))))

	# Mise en forme du menu à vignettes
	menu_vign = '<div class="thumbnails-row">{}</div>'.format(''.join(tab_lg)) if len(tab_lg) > 0 else ''

	return safe(menu_vign)

'''
Initialisation des messages d'erreur
_form : Formulaire source
_sv : Dois-je ajouter un style visuel ?
'''
def init_mess_err(_form, _sv = True) :

	# Import
	from django.conf import settings

	for elem in _form.fields.keys() :
		for cle, val in settings.ERROR_MESSAGES.items() : _form.fields[elem].error_messages[cle] = val

		# Ajout d'un style visuel si le champ est requis
		if _sv == True and _form.fields[elem].required == True :
			spl = _form.fields[elem].label.split('|')
			spl[0] = spl[0] + '<span class="required-field"></span>'
			_form.fields[elem].label = '|'.join(spl)

'''
Initialisation d'une tranche de dates d'absence
_tab : Tableau associatif normé
Retourne un tableau associatif
'''
def init_tranche_dt_abs(_tab) :

	# Imports
	from app.functions import est_ouvr
	from datetime import timedelta

	tab_dt_abs = []
	if _tab :

		# Initialisation des dates potentielles d'absence
		deb = _tab['dt_abs'][0]
		fin = _tab['dt_abs'][-1]
		tab_tranche_dt_abs = [deb + timedelta(elem) for elem in range((fin - deb).days + 1)]

		# Préparation des données d'absence (avec épuration des jours non-ouvrables)
		for index, elem in enumerate(tab_tranche_dt_abs) :
			if est_ouvr(elem) == True :
				if index == 0 :
					indisp_dt_abs = _tab['indisp_abs'][0]
				elif index == len(tab_tranche_dt_abs) - 1 :
					indisp_dt_abs = _tab['indisp_abs'][-1]
				else :
					indisp_dt_abs = 'WD'
				tab_dt_abs.append({ 'dt_abs' : elem, 'indisp_dt_abs' : indisp_dt_abs })

	return tab_dt_abs

'''
Obtention d'une vignette
_tab : Tableau
_tab_cles : Tableau de clés du tableau _tab
Retourne une chaîne de caractères
'''
def init_vign(_tab, _tab_cles) :
	return '''
	<a class="custom-thumbnail" href="{0}">
		<img src="{1}">
		<div>{2}</div>
	</a>
	'''.format(_tab[_tab_cles[0]], _tab[_tab_cles[1]], _tab[_tab_cles[2]])

'''
Préparation d'une datatable
_dtab : Code HTML de la datatable
Retourne une réponse HTTP
'''
def prep_dtab(_dtab, _tab_params = {}) :

	# Imports
	from bs4 import BeautifulSoup
	from django.http import HttpResponse
	import json

	# Obtention d'un objet "BeautifulSoup"
	bs = BeautifulSoup(_dtab, 'html.parser')

	# Initialisation des données de la datatable
	tab_tr = bs.find_all('tbody')[0].find_all('tr')
	tab = [
		[''.join([str(elem) for elem in td.contents if elem != '\n']) for td in tr.find_all('td')] for tr in tab_tr
	]

	# Préparation des données de sortie
	tab_success = { cle : val for cle, val in _tab_params.items() }
	tab_success['datatable'] = tab
	tab_success['datatable_key'] = bs.find_all('div', { 'class' : 'custom-table'})[0]['id'][5:]

	return HttpResponse(json.dumps({ 'success' : tab_success }), content_type = 'application/json')

'''
Définition d'un handler
_req : Objet "requête"
_sc : Code d'erreur (status code)
_mess : Message d'erreur
Retourne une réponse HTTP
'''
def set_handler(_req, _sc, _mess) :

	# Imports
	from app.apps import AppConfig
	from django.shortcuts import render_to_response
	from django.template import RequestContext

	output = render_to_response(
		'./handlers/template.html', 
		RequestContext(_req, { 
			'app_name' : AppConfig.verbose_name,
			'message' : _mess, 
			'title' : 'Erreur {}'.format(_sc)
		})
	)
	output.status_code = _sc

	return output

''' 
Suppression des doublons d'un tableau
_tab : Tableau
Retourne un tableau
'''
def suppr_doubl(_tab) :

	output = []

	# Initialisation d'un ensemble vide
	tab_tuples = set()

	for elem in _tab :
		tupl = tuple(elem)
		if tupl not in tab_tuples : output.append(tupl); tab_tuples.add(tupl)

	return output

'''
Transformation d'un booléen en langage courant
_val : Valeur booléenne
Retourne une chaîne de caractères
'''
def transform_bool(_val) : return 'Oui' if _val == True else 'Non'