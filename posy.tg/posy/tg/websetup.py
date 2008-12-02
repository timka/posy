"""Setup the posy.tg application"""
import logging

#import transaction
from paste.deploy import appconfig
#from tg import config

from posy.tg.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup posy.tg here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    #from posy.tg import model
    #print "Creating tables"
    #model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)


    #transaction.commit()
    #print "Successfully setup"
