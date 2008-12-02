
# -*- coding: utf-8 -*-
"""The application's Globals object"""
import atexit
import logging

import pylons
import tg
from paste.httpserver import ThreadPool
from posy.tg.lib.widgets import langform, languages


class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """
    langform = langform

    def get_lang(self):
        try:
            pylons_lang = pylons.i18n.get_lang()[0]
        except (IndexError, TypeError):
            pylons_lang = 'en'
        lang = tg.session.get('lang', pylons_lang)
        return lang

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """
        self._thread_pool = None

    def add_task(self, runable):
        self.thread_pool.add_task(runable)

    def get_thread_pool(self):
        if self._thread_pool is None:
            self._thread_pool = self._make_thread_pool()
            atexit.register(self._thread_pool.shutdown)

            # XXX: atexit doesn't seem to work at all. Why?
            #import sys
            #atexit.register(lambda: sys.stderr.write('shutting down\n'))
            #sys.stderr.write('registered shutdown callback\n')

        return self._thread_pool
    
    thread_pool = property(get_thread_pool)

    def _make_thread_pool(self):
        pool = pylons.request.environ.get('paste.httpserver.thread_pool')
        if pool is None:
            pool = ThreadPool(nworkers=4, name="PosyThreadPool",
                daemon=False,

                # threads are killed after this many requests
                max_requests=40,

                # when a thread is marked "hung"
                hung_thread_limit=30,

                # when you kill that hung thread
                kill_thread_limit=1800,

                # seconds that a kill should take to go into effect (longer than
                # this and the thread is a "zombie")
                dying_limit=300,

                # spawn if there's too many hung threads
                spawn_if_under=2,

                # when to give up on the process
                max_zombie_threads_before_die=0,

                # every 100 requests check for hung workers
                hung_check_period=100,
                logger=logging.getLogger('.'.join([__name__, 'thread_pool'])),
            )
        return pool
