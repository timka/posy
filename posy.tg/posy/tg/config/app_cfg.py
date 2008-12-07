# -*- coding: utf-8 -*-

from tg import config
from tg.configuration import AppConfig, Bunch
from pylons.i18n import ugettext
from tw.api import make_middleware as tw_middleware

import posy.tg
import posy.tg.lib.app_globals
import posy.tg.lib.helpers
 

class PosyAppConfig(AppConfig):
    # No database — no transaction manager needed
    def add_tm_middleware(self, app):
        return app

    # XXX Fix for Genshi i18n in TG2
    # http://trac.turbogears.org/ticket/2001
    def setup_default_renderer(self):
        from genshi.filters import Translator

        def template_loaded(template): 
            template.filters.insert(0, Translator(ugettext))

        options = {
            "genshi.loader_callback": template_loaded,
            "genshi.default_format": "xhtml",
        }
        config['buffet.template_options'].update(options)
        super(PosyAppConfig, self).setup_default_renderer()

    # XXX Fix for ToscaWidgets i18n in TG2
    # http://trac.turbogears.org/ticket/1999
    def add_tosca_middleware(self, app):
        """Configure the ToscaWidgets middleware"""
        app = tw_middleware(app, {
            'toscawidgets.framework.translator': ugettext,
            'toscawidgets.framework.default_view': self.default_renderer,
            'toscawidgets.middleware.inject_resources': True,
            })
        return app

base_config = PosyAppConfig()
base_config.renderers = []

base_config.package = posy.tg

# XXX This is required to be True (the default) until dotted notation
# is implemented for new TG2 Pylons-style renderers
# http://trac.turbogears.org/ticket/1942
#base_config.use_legacy_renderer = False

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi') 

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = False
