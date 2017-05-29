/**
 * Ajout d'un style visuel à un champ erroné
 * _champ : Objet "champ"
 */
function ajout_erreur(_champ) {
	_champ.addClass('invalid-field');
}

/**
 * Initialisation d'une datatable
 * _dtab : Élémént <div/> enveloppant la datatable
 * _tab : Tableau d'options
 * Retourne un objet "datatable"
 */
function init_dtab(_dtab, _tab = [false, [], [], []]) {

	// Ajustement dynamique de certaines colonnes
	$(_dtab + ' table th').each(function(_index) {
		if ($.inArray(_index, _tab[2]) > -1) {
			$(this).css({ 'width' : '1%' });
		}
	});

	return $(_dtab).find('table').DataTable({
		'aoColumnDefs' : [{
			'aTargets' : _tab[1], 'bSortable' : false
		}, {
			className : 'unbordered', 'targets' : _tab[3]
		}],
		'autoWidth' : false,
		'info' : false,
		'language' : {
			'emptyTable' : 'Aucun enregistrement',
			'lengthMenu': 'Afficher _MENU_ enregistrements',
			'paginate' : { 'next' : 'Suivant', 'previous' : 'Précédent' }
		},
		'lengthMenu' : [[-1, 10, 25, 50], ['---------', 10, 25, 50]],
		'order' : [],
		'paging' : _tab[0],
		'searching' : false
	});
}

/**
 * Redirection tout en affichant un message de succès dans une fenêtre modale
 * _suff : Suffixe d'une fenêtre modale
 * _mess : Message de succès
 * _href : URL de redirection
 */
function redirig_via_fm(_suff, _mess, _href) {

	// Suppression du contenu existant
	$('#za_fm_' + _suff).empty();

	// Insertion d'un nouveau contenu
	var div = $('<div/>', { 'class' : 'valid-form', html : _mess });
	$('#za_fm_' + _suff).append(div);

	// Affichage d'une fenêtre modale
	$('#fm_' + _suff).find('.close').remove();
	$('#fm_' + _suff).modal();

	// Redirection
	setTimeout(function() {
		if (_href == '__reload__') {
			window.location.reload();
		}
		else {
			window.location.href = _href;
		}
	}, 2000);
}

/**
 * Suppression du style visuel préalablement ajouté aux champs erronés (complémentaire à la procédure ajout_erreur)
 * _form : Objet "formulaire"
 */
function suppr_erreurs(_form) {
	_form.find('.invalid-field').each(function() {
		$(this).removeClass('invalid-field');
	});
}

/**
 * Traitement d'une requête GET
 * _e : Objet "event"
 * _suff : Suffixe d'une fenêtre modale
 */
function trait_get(_e, _suff) {

	// Obtention d'un élément du DOM
	var obj = $(_e.target);

	// Stockage de la valeur de l'attribut "onclick"
	var get_onclick = obj.attr('onclick');

	// Désactivation de l'événement "onclick"
	obj.removeAttr('onclick');

	// Lancement d'une requête AJAX
	var data_glob;
	$.getJSON(obj.attr('action'), function(data) {
		data_glob = data;
	}).fail(function(xhr) {
		alert('Erreur ' + xhr.status);
	}).always(function() {

		if (data_glob != undefined) {
			if (data_glob['success']) {

				// Traitement d'une opération avec redirection
				if (data_glob['success']['message'] && data_glob['success']['redirect']) {
					redirig_via_fm(_suff, data_glob['success']['message'], data_glob['success']['redirect']);
				}

				// Affichage d'un contenu
				if (data_glob['success']['content']) {
					if (_suff == null && data_glob['success']['selector']) {

						// Écrasement d'un contenu
						$(data_glob['success']['selector']).html(data_glob['success']['content']);
					}
					else {
						// Suppression du contenu existant
						$('#za_fm_' + _suff).empty();

						// Insertion d'un nouveau contenu
						$('#za_fm_' + _suff).append(data_glob['success']['content']);

						// Affichage d'une fenêtre modale
						$('#fm_' + _suff).modal();
					}
				}

				// Actualisation d'une datatable
				if (data_glob['success']['datatable'] && data_glob['success']['datatable_key']) {

					// Obtention de l'objet "datatable"
					var dtab = tab_dtab[data_glob['success']['datatable_key']];

					// Nettoyage de la datatable
					dtab.clear().draw();

					for (var i = 0; i < data_glob['success']['datatable'].length; i += 1) {

						// Stockage de données
						var elem = data_glob['success']['datatable'][i];

						// Préparation d'une nouvelle ligne de la datatable
						var lg = [];
						for (var j = 0; j < elem.length; j += 1) {
							lg.push(elem[j]);
						}

						// Ajout d'une ligne à la datatable
						dtab.row.add(lg).draw(true);
					}

					// Affichage/désaffichage d'une fenêtre modale
					if (data_glob['success']['modal_id'] && data_glob['success']['modal_id_action']) {
						$(data_glob['success']['modal_id']).modal(data_glob['success']['modal_id_action']);
					}
				}
			}
		}

		// Réactivation de l'événement "onclick"
		obj.attr('onclick', get_onclick);
	});
}

/**
 * Traitement d'une requête POST
 * _e : Objet "event"
 * _tab : Tableau associatif
 */
function trait_post(_e, _tab = {}) {

	// Bloquage du comportement par défaut du formulaire
	_e.preventDefault();

	// Obtention d'un l'objet "formulaire"
	var obj_form = $(_e.target);

	// Définition de l'URL traitant la requête
	var action = obj_form.attr('action');
	if (_tab['action'] != undefined) {
		action += _tab['action'];
	}

	// Définition du suffixe de la fenêtre modale cible
	var suff = obj_form.attr('name').substring(5);
	if (_tab['suffixe'] != undefined) {
		suff = _tab['suffixe'];
	}

	// Stockage de la valeur de l'attribut "onsubmit"
	var get_onsubmit = obj_form.attr('onsubmit');

	// Lancement d'une requête AJAX
	var data_glob;
	$.ajax({
		url : action,
		type : 'post',
		data : new FormData(obj_form.get(0)),
		dataType : 'json',
		processData : false,
		contentType : false,
		beforeSend : function() {

			// Désactivation de l'événement "onsubmit"
			obj_form.attr('onsubmit', 'return false;');
		},
		success : function(data) {
			data_glob = data;	
		},
		error : function(xhr) {
			alert('Erreur ' + xhr.status);
		},
		complete : function() {

			// Suppression des anciennes erreurs
			$('#za_fe_' + suff).remove();
			obj_form.find('.field-error-message').empty();
			suppr_erreurs(obj_form);

			if (data_glob != undefined) {
				if (data_glob['success']) {

					// Traitement d'une opération avec redirection
					if (data_glob['success']['redirect']) {
						if (data_glob['success']['message']) {
							redirig_via_fm(suff, data_glob['success']['message'], data_glob['success']['redirect']);
						}
						else {
							window.location.href = data_glob['success']['redirect'];
						}
					}

					// Affichage d'un contenu dans une fenêtre modale
					if (data_glob['success']['content']) {

						// Suppression du contenu existant
						$('#za_fm_' + suff).empty();

						// Insertion d'un nouveau contenu
						$('#za_fm_' + suff).append(data_glob['success']['content']);

						// Affichage d'une fenêtre modale
						$('#fm_' + suff).modal();
					}

					// Affichage d'un contenu issu d'un formulaire de filtrage présent dans une fenêtre modale
					if (data_glob['success']['mf_content'] && data_glob['success']['selector']) {

						// Fermeture d'une fenêtre modale
						$('#fm_' + suff).modal('hide');

						// Écrasement d'un contenu
						$(data_glob['success']['selector']).html(data_glob['success']['mf_content']);
					}

					// Actualisation d'une datatable
					if (data_glob['success']['datatable'] && data_glob['success']['datatable_key']) {

						// Obtention de l'objet "datatable"
						var dtab = tab_dtab[data_glob['success']['datatable_key']];

						// Nettoyage de la datatable
						dtab.clear().draw();

						for (var i = 0; i < data_glob['success']['datatable'].length; i += 1) {

							// Stockage de données
							var elem = data_glob['success']['datatable'][i];

							// Préparation d'une nouvelle ligne de la datatable
							var lg = [];
							for (var j = 0; j < elem.length; j += 1) {
								lg.push(elem[j]);
							}

							// Ajout d'une ligne à la datatable
							dtab.row.add(lg).draw(true);
						}

						// Affichage/désaffichage d'une fenêtre modale
						if (data_glob['success']['modal_id'] && data_glob['success']['modal_id_action']) {
							$(data_glob['success']['modal_id']).modal(data_glob['success']['modal_id_action']);
						}
					}
				}
				else {
					var erreur_glob;
					for (var champ in data_glob) {
						if (champ.indexOf('__all__') > -1) {

							// Définition du message d'erreur global
							erreur_glob = data_glob[champ][0];
						}
						else {

							// Préparation du message d'erreur
							var ul = $('<ul/>');
							var li = $('<li/>', { html : data_glob[champ][0] });

							// Affichage du message d'erreur
							$('#fw_' + champ).find('.field-error-message').append(ul);
							ul.append(li);
							ajout_erreur($('#id_' + champ));
						}
					}

					// Affichage du message d'erreur global si défini 
					if (erreur_glob != undefined) {
						var div = $('<div/>', {
							'class' : 'custom-alert-danger form-error row',
							'id' : 'za_fe_' + suff,
							html : erreur_glob
						});
						obj_form.closest('.form-root').prepend(div);
					}
				}
			}

			// Réactivation de l'événement "onsubmit"
			obj_form.attr('onsubmit', get_onsubmit);
		}
	});
}