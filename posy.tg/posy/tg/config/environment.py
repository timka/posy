import logging
from posy.tg.config.app_cfg import base_config

#Use base_config to setup the environment loader function
base_load_environment = base_config.make_load_environment()

def load_environment(global_conf, app_conf):
    from tg import config
    base_load_environment(global_conf, app_conf)
    logging.debug('genshi loader callback: %s', config['pylons.app_globals'].genshi_loader.callback)
    from genshi.filters import Translator
    from pylons.i18n import _

    def template_loaded(template):
        logging.debug('template_loaded: %s', locals())
        template.filters.insert(0, Translator(_))

    options = {"genshi.loader_callback": template_loaded}
    # options.update(options_from_config_file)
    config.add_template_engine("genshi", "posy.tg.templates", options) 
