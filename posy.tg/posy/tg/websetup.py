"""Setup the posy.tg application"""
import logging

from paste.deploy import appconfig

from posy.tg.config.environment import load_environment
log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup posy.tg here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
