# coding: utf-8

# Imports
from app.forms.admin import *
from app.models import *
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

# Rafraîchissement des options
admin.site.disable_action('delete_selected')

class Annee(admin.ModelAdmin) :

	def get_readonly_fields(self, _req, _obj = None) :
		if _obj : return self.readonly_fields + ('num_annee',)
		return self.readonly_fields

	# Mise en forme des deux dernières colonnes
	def plage_conges_annee__str(self, _obj) : return ' - '.join(_obj.get_plage_conges_annee__str())
	plage_conges_annee__str.allow_tags = True
	plage_conges_annee__str.short_description = 'Plage de prise des congés payés'

	def plage_rtt_annee__str(self, _obj) : return ' - '.join(_obj.get_plage_rtt_annee__str())
	plage_rtt_annee__str.allow_tags = True
	plage_rtt_annee__str.short_description = 'Plage de prise des RTT'
	
	actions = [admin.actions.delete_selected]
	fields = ['num_annee']
	list_display = ['num_annee', 'plage_conges_annee__str', 'plage_rtt_annee__str']

	def save_model(self, request, obj, form, change) :

		# Imports
		from app.models import TUtilisateur
		from datetime import date

		# Préparation des plages
		obj.plage_conges_annee = [date(obj.num_annee, 1, 1), date(obj.num_annee + 1, 5, 31)]
		obj.plage_rtt_annee = [date(obj.num_annee, 1, 1), date(obj.num_annee, 12, 31)]

		super(Annee, self).save_model(request, obj, form, change)

		# Calcul des proratas
		for u in TUtilisateur.objects.all() : u.calc_proratas()

admin.site.register(TAnnee, Annee)

class GroupeUtilisateur(admin.ModelAdmin) :

	# Mise en forme de la dernière colonne
	def gpe_util__count(self, _obj) : return _obj.get_util_set().count()
	gpe_util__count.allow_tags = True; gpe_util__count.short_description = 'Nombre d\'utilisateurs composant le groupe'

	actions = [admin.actions.delete_selected]
	fields = ['int_gpe_util', 'util']
	form = FGroupeUtilisateur
	list_display = ['int_gpe_util', 'gpe_util__count']

admin.site.register(TGroupeUtilisateur, GroupeUtilisateur)

class Utilisateur(UserAdmin) :

	# Déclaration des actions supplémentaires
	def set_en_act__on(_madmin, _req, _qs) : _qs.update(en_act = True)
	set_en_act__on.short_description = 'Rendre les T_UTILISATEUR sélectionnés en activité'

	def set_en_act__off(_madmin, _req, _qs) : _qs.update(en_act = False)
	set_en_act__off.short_description = 'Rendre les T_UTILISATEUR sélectionnés en inactivité'

	actions = [set_en_act__on, set_en_act__off, admin.actions.delete_selected]
	add_fieldsets = [
		['Données personnelles', { 'fields' : [('last_name'), ('first_name'), ('email')] }],
		['Données générales du compte', { 'fields' : [('username'), ('zs_password'), ('zs_password_bis')] }],
		['Options du compte', { 'fields' : [('is_active'), ('is_staff'), ('is_superuser')] }]
	]
	add_form = FUtilisateurCreate
	fieldsets = [
		['Données personnelles', { 'fields' : [('last_name'), ('first_name'), ('email')] }],
		['Données générales du compte', { 'fields' : [('username'), ('password')] }],
		['Options du compte', { 'fields' : [('is_active'), ('is_staff'), ('is_superuser')] }]
	]
	form = FUtilisateurUpdate
	list_display = ['username', 'last_name', 'first_name', 'email', 'en_act', 'is_active', 'last_login']
	list_filter = [('en_act', admin.BooleanFieldListFilter)]

admin.site.register(TUtilisateur, Utilisateur)

# Retrait des fonctionnalités d'origine
admin.site.unregister(User)
admin.site.unregister(Group)

class BonusMalusUtilisateur(admin.ModelAdmin) :

	# Mise en forme de la première colonne
	def pk__str(self, _obj) : return _obj
	pk__str.allow_tags = True; pk__str.short_description = 'Couple agent concerné/année'

	actions = [admin.actions.delete_selected]
	fields = ['id_util', 'num_annee', 'int_bm_util', 'nbre_conges_bm_util', 'nbre_rtt_bm_util']
	list_display = ['pk__str', 'int_bm_util', 'nbre_conges_bm_util', 'nbre_rtt_bm_util']

admin.site.register(TBonusMalusUtilisateur, BonusMalusUtilisateur)

class GroupeTypeAbsence(admin.ModelAdmin) :
	actions = [admin.actions.delete_selected]
	fieldsets = [
		['Données générales', { 'fields' : [('int_gpe_type_abs'), ('abrev_gpe_type_abs'), ('code_type_util')] }],
		['Données complémentaires', { 'fields' : [('coul_gpe_type_abs')] }],
		['Paramétrage de la liste déroulante', { 'fields' : [('est_disp'), ('ordre_zl_gpe_type_abs')] }]
	]
	list_display = ['int_gpe_type_abs', 'abrev_gpe_type_abs', 'code_type_util', 'coul_gpe_type_abs']
	ordering = ['int_gpe_type_abs']

admin.site.register(TGroupeTypeAbsence, GroupeTypeAbsence)

class GroupeTypeAbsenceFilter(SimpleListFilter) :

	title = 'Groupe de type d\'absence'
	parameter_name = 'id_gpe_type_abs'

	def lookups(self, _req, _madmin) :
		return [*_madmin.get_queryset(_req).values_list(
			'id_gpe_type_abs', 'id_gpe_type_abs__int_gpe_type_abs'
		).distinct().order_by('id_gpe_type_abs__int_gpe_type_abs')]

	def queryset(self, _req, _qs) :
		if self.value() : return _qs.filter(id_gpe_type_abs__id_gpe_type_abs__exact = self.value())

class TypeAbsence(admin.ModelAdmin) :
	actions = [admin.actions.delete_selected]
	fields = ['int_type_abs', 'id_gpe_type_abs', 'lmt_type_abs', 'pj_abs_req', 'descr_nds_type_abs']
	list_display = ['int_type_abs', 'id_gpe_type_abs', 'lmt_type_abs']
	list_filter = [GroupeTypeAbsenceFilter]

admin.site.register(TTypeAbsence, TypeAbsence)

class Absence(admin.ModelAdmin) :

	# Déclaration des actions supplémentaires
	def set_src_alerte__on(_madmin, _req, _qs) : _qs.update(src_alerte = True)
	set_src_alerte__on.short_description = 'Rendre les T_ABSENCE sélectionnées alertables'

	def set_src_alerte__off(_madmin, _req, _qs) : _qs.update(src_alerte = False)
	set_src_alerte__off.short_description = 'Rendre les T_ABSENCE sélectionnées non-alertables'

	# Mise en forme de la première colonne
	def pk__str(self, _obj) : return _obj
	pk__str.allow_tags = True; pk__str.short_description = 'Couple agent concerné/année/type d\'absence'

	# Mise en forme de la seconde colonne
	def dt_abs__fr_str(self, _obj) : return _obj.get_dt_abs__fr_str()
	dt_abs__fr_str.allow_tags = True; dt_abs__fr_str.short_description = 'Date(s) d\'absence' 

	def has_add_permission(self, _req) : return False
	def has_delete_permission(self, _req, _obj = None) : return False

	actions = [set_src_alerte__on, set_src_alerte__off]
	fields = ['src_alerte']
	list_display = ['pk__str', 'dt_abs__fr_str', 'src_alerte']

admin.site.register(TAbsence, Absence)

class DateFermeture(admin.ModelAdmin) :

	# Mise en forme de la première colonne
	def pk__str(self, _obj) : return _obj
	pk__str.allow_tags = True; pk__str.short_description = 'Date de fermeture exceptionnelle'

	actions = [admin.actions.delete_selected]
	fields = ['id_dt_ferm']
	list_display = ['pk__str']

admin.site.register(TDateFermeture, DateFermeture)