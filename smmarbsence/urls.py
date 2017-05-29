# coding: utf-8

# Imports
from app.apps import AppConfig
from app.views import alert
from app.views import cal_abs
from app.views import gest_abs
from app.views import gest_agents
from app.views import gest_compte
from app.views import handlers
from app.views import index
from app.views import mess
from app.views import real_etats
from django.conf import settings
from django.conf.urls import handler403
from django.conf.urls import handler404
from django.conf.urls import handler500
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index.html$', index.index, name = 'index'),
    url(r'^$', index.index, name = 'index')
]

urlpatterns += [
    url(r'^messagerie/$', mess.get_mess, name = 'get_mess'),
    url(r'^messagerie/consulter-message/([0-9]+)/$', mess.consult_mess, name = 'consult_mess')
]

urlpatterns += [url(r'^alertes/$', alert.get_alert, name = 'get_alert')]

# Détermination de l'URL pour chacun des modules
mod_url = 'modules/'
gest_compte_url = mod_url + 'gestion-compte/'
gest_agents_url = mod_url + 'gestion-agents/'
gest_abs_url = mod_url + 'gestion-absences/'
cal_abs_url = mod_url + 'calendrier-absences/'
real_etats_url = mod_url + 'realisation-etats/'

urlpatterns += [
    url(r'^{}consulter-compte/$'.format(gest_compte_url), gest_compte.consult_compte, name = 'consult_compte'),
    url(r'^{}modifier-compte/$'.format(gest_compte_url), gest_compte.modif_compte, name = 'modif_compte')
]

urlpatterns += [
    url(r'^{}$'.format(gest_agents_url), gest_agents.get_menu, name = 'gest_agents'),
    url(
        r'^{}ajouter-agent/$'.format(gest_agents_url), gest_agents.ger_agent, { '_inst' : False }, name = 'ajout_agent'
    ),
    url(
        r'^{}modifier-agent/$'.format(gest_agents_url), gest_agents.ger_agent, { '_inst' : True }, name = 'modif_agent'
    ),
    url(r'^{}choisir-agent/$'.format(gest_agents_url), gest_agents.chois_agent, name = 'chois_agent'),
    url(r'^{}consulter-agent/([0-9]+)/$'.format(gest_agents_url), gest_agents.consult_agent, name = 'consult_agent')
]

urlpatterns += [
    url(r'^{}$'.format(gest_abs_url), gest_abs.get_menu, name = 'gest_abs'),
    url(r'^{}ajouter-absence/$'.format(gest_abs_url), gest_abs.ger_abs, name = 'ajout_abs'),
    url(r'^{}choisir-absence/$'.format(gest_abs_url), gest_abs.chois_abs, name = 'chois_abs'),
    url(r'^{}consulter-absence/([0-9]+)/$'.format(gest_abs_url), gest_abs.consult_abs, name = 'consult_abs'),
    url(r'^{}choisir-absence-en-attente/$'.format(gest_abs_url), gest_abs.chois_verif_abs, name = 'chois_verif_abs'),
    url(r'^{}verifier-absence/([0-9]+)/$'.format(gest_abs_url), gest_abs.verif_abs, name = 'verif_abs')
]

urlpatterns += [
    url(r'^{}$'.format(cal_abs_url), cal_abs.main, name = 'cal_abs')
]

urlpatterns += [
    url(r'^{}$'.format(real_etats_url), real_etats.get_menu, name = 'real_etats'),
    url(
        r'^{}selectionnant-absences/$'.format(real_etats_url),
        real_etats.filtr_abs,
        { '_gby' : False },
        name = 'select_abs'
    ),
    url(
        r'^{}regroupant-absences/$'.format(real_etats_url),
        real_etats.filtr_abs,
        { '_gby' : True },
        name = 'regroup_abs'
    ),
]

# Possibilité de consulter les pièces jointes
if settings.DEBUG is True : urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

# Détermination des templates personnalisés pour certains codes d'erreur
handler403 = handlers.handler_403
handler404 = handlers.handler_404
handler500 = handlers.handler_500

# Détermination de certains paramètres du site d'administration
admin.site.index_title = 'Accueil'
admin.site.site_header = 'Administration de {}'.format(AppConfig.verbose_name)
admin.site.site_title = 'Site d\'administration de {}'.format(AppConfig.verbose_name)