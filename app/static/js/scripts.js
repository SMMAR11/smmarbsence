// Variables globales
var tab_dtab = {};

/**
 * Affiche un loader dès la fin du chargement du DOM
 */
$(document).ready(function() {

	// Désaffichage de la page HTML (leurre)
	$('.container-fluid').hide();
	$('body').css({ 'background-color' : '#FFF', 'margin-bottom' : 0 });

	// Stockage du contenu du loader
	var tab_cont_load = [
		$('<span/>', { 'class' : 'fa fa-circle-o-notch fa-spin' }),
		$('<br/>'),
		'Chargement de la page'
	];

	// Préparation du loader (centré verticalement)
	var tab_divs = [
		$('<div/>', { 'id' : 'main-loader' }),
		$('<div/>')
	]
	for (var i = 0; i < tab_cont_load.length; i += 1) {
		tab_divs[1].append(tab_cont_load[i]);
	}
	tab_divs[1].appendTo(tab_divs[0]);

	// Affichage du loader.
	tab_divs[0].prependTo('body');
});

/**
 * Affiche une page web dès la fin du chargement de celle-ci
 */
$(window).on('load', function() {
	setTimeout(function() {

		// Initialisation des datatables
		tab_dtab = {
			'alert' : init_dtab('#dtab_alert', [false, [0], [0], []]),
			'chois_abs' : init_dtab('#dtab_chois_abs', [false, [5], [5], []]),
			'chois_verif_abs' : init_dtab('#dtab_chois_verif_abs', [false, [3], [3], []]),
			'chois_agent' : init_dtab('#dtab_chois_agent', [false, [5], [5], []]),
			'ChoisirFamilleAbsence-zi_fam_abs' : init_dtab(
				'#dtab_ChoisirFamilleAbsence-zi_fam_abs', [false, [1], [1], []]
			),
			'consult_abs' : init_dtab('#dtab_consult_abs', [false, [5], [5], []]),
			'consult_cet_gest_agent' : init_dtab('#dtab_consult_cet_gest_agent', [false, '_all', [4, 5], [6, 7]]),
			'consult_cet_gest_compte' : init_dtab('#dtab_consult_cet_gest_compte', [false, '_all', [4, 5], []]),
			'consult_decompt_util' : init_dtab('#dtab_consult_decompt_util', [true, '_all', [0], []]),
			'consult_statut_util' : init_dtab('#dtab_consult_statut_util', [false, '_all', [2, 3], []]),
			'FiltrerAbsences-zcc_util' : init_dtab('#dtab_FiltrerAbsences-zcc_util', [false, [1], [1], []]),
			'FiltrerCalendrierAbsences-zcc_gpe_util' : init_dtab(
				'#dtab_FiltrerCalendrierAbsences-zcc_gpe_util', [false, [1], [1], []]
			),
			'FiltrerCalendrierAbsences-zcc_util' : init_dtab(
				'#dtab_FiltrerCalendrierAbsences-zcc_util', [false, [1], [1], []]
			),
			'GererAgent-gpe_util' : init_dtab('#dtab_GererAgent-gpe_util', [false, [1], [1], []]),
			'GererAgent-type_util' : init_dtab('#dtab_GererAgent-type_util', [false, [1], [1], []]),
			'nbre_j_abs_annee' : init_dtab('#dtab_nbre_j_abs_annee', [false, '_all', [], []]),
			'nbre_j_abs_mois' : init_dtab('#dtab_nbre_j_abs_mois', [false, '_all', [], []]),
			'regroup_abs' : init_dtab('#dtab_regroup_abs', [false, [], [], []]),
			'SelectionnerMessagesBdR-zcc_mess_util' : init_dtab(
				'#dtab_SelectionnerMessagesBdR-zcc_mess_util', [true, [0, 1, 5], [0, 1, 5], []]
			),
			'SelectionnerMessagesArchives-zcc_mess_util' : init_dtab(
				'#dtab_SelectionnerMessagesArchives-zcc_mess_util', [true, [0, 1, 5], [0, 1, 5], []]
			),
			'select_abs' : init_dtab('#dtab_select_abs', [false, [5], [5], []])
		};

		// Réinitialisation des formulaires
		$('form').each(function() {
			$(this)[0].reset();
		});

		// Suppression du loader
		$('#main-loader').remove();

		// Affichage de la page HTML
		$('body').removeAttr('style');
		$('.container-fluid').show();
	}, 250);
});

/**
 * Initialise certains éléments du DOM
 */
$(document).on('mousemove', function() {

	// Suppression de l'attribut "required" de chaque champ
	$('form').each(function() {
		for (var i = 0; i < $(this).length; i += 1) {
			var form = $(this)[i];
			for (var j = 0; j < form.length; j += 1) {
				var champ = form[j];
				$(champ).removeAttr('required');
			}
		}
	});

	// Mise en place d'un calendrier sur chaque champ "date"
	$('.date').datepicker({
		autoclose : true,
		endDate : '31/12/2999',
		keyboardNavigation : false,
		language : 'fr',
		maxViewMode : 2,
		orientation : 'bottom right',
		startDate : '01/01/2000'
	});
});

/**
 * Cochage/décochage automatique d'un groupe de cases à cocher
 */
$('input[type="checkbox"]').on('change', function() {

	// Obtention d'un objet "case à cocher"
	var obj = $(this);

	if (obj.val() == '__all__') {

		// Stockage du nom du groupe de cases à cocher
		var get_name = obj.attr('id').substr(3);
		get_name = get_name.substr(0, get_name.length - 5);

		$('input[name="' + get_name + '"]').each(function() {
			if (obj.is(':checked')) {
				this.checked = true;
			}
			else {
				this.checked = false;
			}
		});
	}
	else {

		// Décochage de la case à cocher permettant le cochage/décochage automatique d'un groupe de cases à cocher
		if (obj.is(':checked') == false) {
			$('#id_' + obj.attr('name') + '__all').prop('checked', false);
		}
	}
});

/**
 * Déplacement de messages vers les messages archivés
 */
$('#btn_arch').on('click', function() {
	var obj_form = $('form[name="form_select_mess_bdr"]');
	obj_form.attr('onsubmit', 'trait_post(event, { \'action\' : \'?action=deplacer-vers&ou=messages-archives\' });');
	obj_form.submit();
});

/**
 * Déplacement de messages vers la boîte de réception
 */
$('#btn_depl_vers_bdr').on('click', function() {
	var obj_form = $('form[name="form_select_mess_arch"]');
	obj_form.attr('onsubmit', 'trait_post(event, { \'action\' : \'?action=deplacer-vers&ou=boite-de-reception\' });');
	obj_form.submit();
});

/**
 * Suppression de messages depuis la boîte de réception
 */
$('#btn_suppr_mess_bdr').on('click', function() {
	var obj_form = $('form[name="form_select_mess_bdr"]');
	obj_form.attr(
		'onsubmit',
		`trait_post(event, {
			\'action\' : \'?action=supprimer-messages-etape-1&depuis=boite-de-reception\', \'suffixe\' : \'suppr_mess\'
		});`
	);
	obj_form.submit();
});

/**
 * Suppression de messages depuis les messages archivés
 */
$('#btn_suppr_mess_arch').on('click', function() {
	var obj_form = $('form[name="form_select_mess_arch"]');
	obj_form.attr(
		'onsubmit',
		`trait_post(event, {
			\'action\' : \'?action=supprimer-messages-etape-1&depuis=messages-archives\', \'suffixe\' : \'suppr_mess\' 
		});`
	);
	obj_form.submit();
});

/**
 * Affichage d'un loader avant le lancement d'une requête AJAX
 */
$(document).ajaxSend(function() {

	// Initialisation du loader
	var obj_load = $('<div/>', { 'class' : 'text-center', 'id' : 'ajax-loader' });

	// Stockage du contenu du loader
	var tab_cont_load = [
		$('<span/>', { 'class' : 'fa fa-circle-o-notch fa-spin' }),
		$('<br/>'),
		'Veuillez patienter...'
	];

	// Préparation du loader
	for (var i = 0; i < tab_cont_load.length; i += 1) {
		obj_load.append(tab_cont_load[i]);
	}

	// Affichage du loader
	obj_load.insertAfter('.container-fluid');
});

/**
 * Désaffichage d'un loader dès la fin d'une requête AJAX
 */
$(document).ajaxComplete(function() {
	$('#ajax-loader').remove();
});

/**
 * Obtention du nom d'un fichier uploadé
 */
$(document).on('change', 'input[type="file"]', function() {

	// Obtention d'un élément "field-wrapper"
	var fw = $('#fw_' + $(this).attr('name'));

	// Retrait du nom de l'ancien fichier uploadé
	fw.find('.if-return').remove();

	// Préparation du nom du nouveau fichier uploadé
	var div = $('<div/>', { 'class' : 'if-return' });
	var span = $('<span/>', { 'class' : 'file-infos', html : ' ' + $(this).val() });

	// Affichage du nom du nouveau fichier uploadé
	div.append(span);
	div.insertAfter(fw.find('.if-trigger'));

	// Application d'un style CSS.
	fw.find('.if-trigger').css('margin-right', '3.5px');
});

/**
 * Affichage de la date choisie via le datepicker
 */
$(document).on('change', 'input[name$="__datepicker"]', function() {

	// Stockage de la valeur de la zone de saisie cachée
	var get_name = $(this).attr('name');

	// Transfert de la valeur vers la zone de date
	var id = '#id_' + get_name.substr(0, get_name.length - 12);
	$(id).val($(this).val());
});

/**
 * Gestion d'affichage des champs "date" du formulaire de gestion d'une absence
 */
$('input[name="GererAbsence-rb_dt_abs_tranche"]').on('change', function() {
	if ($(this).val() == 1) {
		$('#za_dt_abs_tranche').hide();
		$('#za_dt_abs').show();
	}
	else {
		$('#za_dt_abs').hide();
		$('#za_dt_abs_tranche').show();
	}
});

/**
 * Clonage du calendrier des absences
 */
$(document).on('click', '#btn_agrand_cal_abs', function() {

	// Stockage de l'en-tête et du corps de la fenêtre modale liée
	var get_title = $('#za_cal_abs .clone-title').clone();
	var get_body = $('#za_cal_abs .clone-body').clone();

	// Mise à jour de l'en-tête et du corps de la fenêtre modale liée
	$('#fm_agrand_cal_abs .modal-title').html(get_title);
	$('#za_fm_agrand_cal_abs').html(get_body);

	// Affichage de la fenêtre modale liée
	$('#fm_agrand_cal_abs').modal();
});

/**
 * Soumission du formulaire de filtrage des absences
 */
$('form[name="form_filtr_abs"]').on('change', function() {
	$(this).submit();
});

/**
 * Soumission du formulaire de filtrage des absences en attente de vérification
 */
$('form[name="form_filtr_verif_abs"]').on('change', function() {
	$(this).submit();
});

/**
 * Épuration des icônes d'alertes (en cas de doublons par onglet)
 */
$(window).on('load', function() {
	$('.nt-icon-wrapper').each(function() {
		if ($(this).find('.nt-icon').length > 1) {
			$(this).find('.nt-icon').each(function(_i) {
				if (_i > 0) {
					$(this).remove();
				}
			});
		}
	});
});

/**
 * Soumission du formulaire de tri des transactions CET d'un agent
 */
$('form[name="form_tri_trans_cet_util"]').on('change', function() {
	$(this).submit();
});

/**
 * Détermination de l'URL finale de téléchargement du CET agent
 */
$('#btn_telech_cet_agent').on('click', function() {

	// Initialisation des paramètres GET de l'URL
	tab_params = {
		'mode-de-tri' : $('#id_zl_mode_tri').val(),
		'historique' : $('#id_zl_hist_trans_cet_util').val()
	}

	// Définition de l'URL
	set_href = $(this).attr('href');
	for (cle in tab_params) {
		set_href += '&' + cle + '=' + tab_params[cle];
	}

	// Application de l'URL définie
	$(this).attr('href', set_href);
});

/**
 * Soumission du formulaire de filtrage des agents
 */
$('form[name="form_filtr_agents"]').on('change', function() {
	$(this).submit();
});