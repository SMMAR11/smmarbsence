# coding: utf-8

# Imports
from app.models import *
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

class FGroupeUtilisateur(forms.ModelForm) :

    # Champ
    util = forms.ModelMultipleChoiceField(
        label = 'Utilisateurs composant le groupe',
        queryset = TUtilisateur.objects.order_by('username'),
        required = False,
        widget = FilteredSelectMultiple('T_UTILISATEUR', is_stacked = False)
    )

    class Meta :
        fields = '__all__'
        model = TGroupeUtilisateur

    def __init__(self, *args, **kwargs) :
        super(FGroupeUtilisateur, self).__init__(*args, **kwargs) 

        # Définition de la valeur initiale du champ personnalisé     
        if self.instance.get_pk() :
             self.fields['util'].initial = [u.get_pk() for u in self.instance.get_util_set().all()]

    def save(self, *args, **kwargs) :

        # Création/modification d'une instance TGroupeUtilisateur
        obj = super(FGroupeUtilisateur, self).save(*args, **kwargs)
        obj.save()

        # Liaison avec la table t_groupes_utilisateur
        obj.get_gpe_util_set().all().delete()
        for u in self.cleaned_data.get('util') : TGroupesUtilisateur.objects.create(id_gpe_util = obj, id_util = u)

        return obj

class FUtilisateurCreate(forms.ModelForm) :

    # Champs
    zs_password = forms.CharField(label = 'Mot de passe', widget = forms.PasswordInput())
    zs_password_bis = forms.CharField(label = 'Confirmation du mot de passe', widget = forms.PasswordInput())

    class Meta :
        fields = [
            'email',
            'first_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_name',
            'username'
        ]
        labels = { 'email' : 'Courriel principal', 'last_name' : 'Nom de famille' }
        model = TUtilisateur

    def __init__(self, *args, **kwargs) :

        # Initialisation des arguments
        self.kw_test = kwargs.pop('kw_test', False)

        super(FUtilisateurCreate, self).__init__(*args, **kwargs)

        # Passage de certains champs à l'état requis
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_zs_password_bis(self) :

        # Stockage des données du formulaire
        val_password = self.cleaned_data.get('zs_password')
        val_password_bis = self.cleaned_data.get('zs_password_bis')

        # Renvoi d'une erreur si non-similitude des mots de passe
        if val_password and val_password_bis and val_password != val_password_bis :
            raise forms.ValidationError('Les mots de passe saisis ne correspondent pas.')

    def save(self, *args, **kwargs) :

        # Création d'une instance TUtilisateur
        obj = super(FUtilisateurCreate, self).save(*args, **kwargs)
        obj.set_password(self.cleaned_data.get('zs_password'))
        obj.save()

        # Liaison obligatoire avec la table t_roles_utilisateur
        if 'A' not in obj.get_type_util__list() :
            TRolesUtilisateur.objects.create(code_type_util = TTypeUtilisateur.objects.get(pk = 'A'), id_util = obj)

        return obj

class FUtilisateurUpdate(forms.ModelForm) :

    # Import
    from django.contrib.auth.forms import ReadOnlyPasswordHashField

    # Champ
    password = ReadOnlyPasswordHashField(
        help_text = '''
        Les mots de passe ne sont pas enregistrés en clair, ce qui ne permet pas d'afficher le mot de passe de cet
        utilisateur, mais il est possible de le changer en utilisant <a href="../password/">ce formulaire</a>.
        ''',
        label = 'Mot de passe'
    )

    class Meta :
        fields = [
            'email',
            'first_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_name',
            'username'
        ]
        labels = { 'email' : 'Courriel principal', 'last_name' : 'Nom de famille' }
        model = TUtilisateur

    def __init__(self, *args, **kwargs) :
        super(FUtilisateurUpdate, self).__init__(*args, **kwargs)

        # Passage de certains champs à l'état requis
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_password(self) : return self.initial['password']

    def save(self, *args, **kwargs) :

        # Modification d'une instance TUtilisateur
        obj = super(FUtilisateurUpdate, self).save(*args, **kwargs).save()

        # Liaison obligatoire avec la table t_roles_utilisateur
        if 'A' not in obj.get_type_util__list() :
            TRolesUtilisateur.objects.create(code_type_util = TTypeUtilisateur.objects.get(pk = 'A'), id_util = obj)

        return obj