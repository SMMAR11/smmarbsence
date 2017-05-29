# coding: utf-8

'''
Obtention du formulaire de gestion des statuts agent
_req : Objet "requête"
_form : Objet "formulaire"
Retourne une chaîne de caractères
'''
def get_ft_ger_statut_util(_req, _form) :

	# Imports
	from app.functions import init_form
	from django.template.context_processors import csrf

	# Initialisation des champs
	form = init_form(_form)

	return '''
	<form action="?action={0}-statut-agent" method="post" name="form_{1}_statut_util" onsubmit="trait_post(event);">
		<input name="csrfmiddlewaretoken" type="hidden" value="{2}">
		{3}
		{4}
		<div class="row">
			<div class="col-sm-6">{5}</div>
			<div class="col-sm-6">{6}</div>
		</div>
		<button class="center-block custom-btn green-btn" type="submit">Valider</button>
	</form>
	'''.format(
		'modifier' if _form.instance.get_pk() else 'ajouter',
		'modif' if _form.instance.get_pk() else 'ajout',
		csrf(_req)['csrf_token'],
		form['zsc_pk'],
		form['statut_util'],
		form['mois_deb_statut_util'],
		form['num_annee']
	)

'''
Obtention du formulaire de gestion des transactions entrantes sur le CET agent
_req : Objet "requête"
_form : Objet "formulaire"
Retourne une chaîne de caractères
'''
def get_ft_ger_trans_cet_util(_req, _form) :

	# Imports
	from app.functions import init_form
	from django.template.context_processors import csrf

	# Initialisation des champs
	form = init_form(_form)

	return '''
	<form action="?action={0}-transaction-entrante-cet-agent" method="post" name="form_{1}_trans_cet_util"
	onsubmit="trait_post(event);">
		<input name="csrfmiddlewaretoken" type="hidden" value="{2}">
		{3}
		{4}
		<div class="row">
			<div class="col-sm-6">{5}</div>
			<div class="col-sm-6">{6}</div>
		</div>
		<button class="center-block custom-btn green-btn" type="submit">Valider</button>
	</form>
	'''.format(
		'modifier' if _form.instance.get_pk() else 'ajouter',
		'modif' if _form.instance.get_pk() else 'ajout',
		csrf(_req)['csrf_token'],
		form['zsc_pk'],
		form['zl_annee'],
		form['nbre_conges_trans_cet_util'],
		form['nbre_rtt_trans_cet_util']
	)