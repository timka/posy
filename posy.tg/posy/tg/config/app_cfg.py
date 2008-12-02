from tg import config
from tg.configuration import AppConfig, Bunch
from pylons.i18n import ugettext
from tw.api import make_middleware as tw_middleware

import posy.tg
import posy.tg.lib.app_globals
import posy.tg.lib.helpers
 

class PosyAppConfig(AppConfig):
    def add_tm_middleware(self, app):
        return app

#    def setup_default_renderer(self):
#        from genshi.filters import Translator

#        def template_loaded(template): 
#            template.filters.insert(0, Translator(ugettext))

#        options = {
#            "genshi.loader_callback": template_loaded,
#            "genshi.default_format": "xhtml",
#        }
#        config['buffet.template_options'].update(options)
#        super(PosyAppConfig, self).setup_default_renderer()

#    def add_tosca_middleware(self, app):
#        """Configure the ToscaWidgets middleware"""
#        app = tw_middleware(app, {
#            'toscawidgets.framework.translator': ugettext,
#            'toscawidgets.framework.default_view': self.default_renderer,
#            'toscawidgets.middleware.inject_resources': True,
#            'toscawidgets.framework': 'pylons',
#            })
#        return app

base_config = PosyAppConfig()
base_config.renderers = []

base_config.package = posy.tg
#base_config.use_legacy_renderer = False

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi') 

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = False
