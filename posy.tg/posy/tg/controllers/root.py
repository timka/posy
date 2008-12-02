"""Main Controller"""
import copy
import types
import logging
import datetime

import tg
import pylons
from tg import session
from tg import expose, flash
from tg import redirect, validate
from tg import config, request
from pylons.i18n import ugettext as _

from posy.api import retrieve_services as posy_services
from posy.tg.lib.base import BaseController
from posy.tg.lib.decorators import check_settings, post_only, https
from posy.tg.lib.menu import Menu
from posy.tg.lib.util import send_email, path_join, password_dict, clear_passwords
from posy.tg.lib.widgets import (posy_form, settings_forms, langform)


class RootController(BaseController):
    @expose('posy.tg.templates.index')
    @check_settings()
    def index(self, *args, **kw):
        tg.tmpl_context.form = posy_form
        return dict(form_data=dict(action=tg.url('/update')))

    @validate(form=posy_form, error_handler=index)
    @expose()
    @post_only()
    @check_settings()
    def update(self, content=None, timestamp=None, **kw):
        logging.debug('when: %s', timestamp)
        session_data = copy.deepcopy(dict(session))
        tg.g.add_task(lambda: self.update_task(session=session_data,
            content=content,
            datetime=timestamp)
        )
        flash(_('Message sent'))
        redirect(tg.url('/'))

    def update_task(self, session, content, **kw):
        # Setup emailing
        email = session['settings'].get('general', {}).get('email')
        email_messages = []

        logging.debug('update_task: session: %s', session)
        logging.debug('update_task: kw: %s', kw)

        email_messages.append('content: %s' % content)
        email_messages.append('settings: %s' % session['settings'])

        for name, service in posy_services():
            if name not in session['settings']:
                message = 'No settings for service %r. Skipping.' % name
                email_messages.append(message)
                continue

            settings = session['settings'][name]

            if not settings.get('enable'):
                message = 'Service %r not enabled. Skipping.' % name
                email_messages.append(message)
                continue

            username = settings.get('username')
            if not username:
                message = 'Username for %r is not set. Skipping.' % name
                email_messages.append(message)
                continue

            password = settings.get('password')
            if not password:
                message = 'Password for %r is not set. Skipping.' % name
                email_messages.append(message)
                continue

            try:
                service(username, password or '').update(content, **kw)
            except Exception, e:
                message = 'Error updating %r: %s\n: %s' % (name, type(e), e)
                email_messages.append(message)
                logging.error(message)

        if not email:
            return
        if not email_messages:
            return
        send_email(email_messages, email, config.get('error_email_from',
            'posy@localhost'), 'Posy debugging')

    @expose('posy.tg.templates.about')
    def about(self):
        return dict()

    @expose()
    @validate(form=langform)
    def lang(self, lang=None):
        redirect_url = pylons.request.referrer or tg.url('/')
        if not lang:
            redirect(tg.url(redirect_url))
        session['lang'] = lang
        session.save()
        redirect(tg.url(redirect_url))


class SettingsMenu(Menu):
    base = tg.url('/settings')

    @classmethod
    def make_controller(cls, name):
        form = settings_forms.get(name)
        return SettingsController(name, form)


class SettingsBaseController(BaseController):
    menu = SettingsMenu()


class SettingsRootController(SettingsBaseController):
    @https()
    @expose()
    def index(self, *args, **kw):
        '''
        Find first not set up service
        '''
        for name, item in self.menu:
            if name in session.get('skip', set()):
                continue
            if name not in session.get('settings', {}):
                redirect(item.url)
        # Redirect to the first item in list
        # redirect(self.menu[0][1].url)

        # Redirect to the last item in list
        redirect(item.url)

    @https()
    @expose()
    def clear(self):
        session.pop('settings', None)
        session.pop('skip', None)
        session.pop('lang', None)
        session.save()
        logging.debug('clear all settings: session: %s', session)
        flash(_('All settings cleared'))
        redirect(self.menu.base)

    @https()
    @expose()
    def lookup(self, *remainder):
        try:
            name = remainder[0]
            controller = self.menu[name].controller
        except LookupError:
            raise tg.exceptions.HTTPNotFound
        return controller, remainder[1:]

RootController.settings = SettingsRootController()


class SettingsController(SettingsBaseController):
    def __new__(cls, name, form):
        '''
        Set up validation dynamically
        '''
        instance = SettingsBaseController.__new__(cls)
        instance.form = form
        update = instance.update.im_func
        index = instance.index.im_func
        update = validate(form=form, error_handler=index)(update)
        update = types.MethodType(update, instance, cls)
        instance.update = update
        return instance

    def __init__(self, name, form):
        self.name = name

    @property
    def url(self):
        return self.menu[self.name].url

    @https()
    @expose('posy.tg.templates.settings')
    def index(self, *args, **kw):
        tg.tmpl_context.form = self.form

        base = self.menu.base
        settings = dict(session).get('settings', {})
        form_data = clear_passwords(settings)
        form_data.setdefault(self.name, {})
        form_data[self.name].setdefault('enable', False)

        form_args = {
            'action': path_join(base, self.name, 'update'),
        }

        form_args['child_args'] = {
            'buttons': {
                'child_args': {
                    'clear': {
                        'url': path_join(base, self.name, 'clear'),
                    },
                    'skip': {
                        'url': path_join(base, self.name, 'skip'),
                        #'disabled': not self.menu[self.name].is_new
                    },
                    'clear_all': {
                        'url': path_join(base, 'clear'),
                    }
                }
            }
        }
        menu = list(self.make_menu())
        return dict(form_data=form_data, form_args=form_args, menu=menu)

    def make_menu(self):
        for name, item in self.menu:
            # Mark current menu item
            selected = self.name == name
            yield item, selected

    @expose()
    @post_only()
    def update(self, *args, **kw):
        # Make sure passwords won't leak from session
        session.setdefault('settings', password_dict({}))

        # This is the first time this service is set up
        first_time = self.name not in session['settings']

        session['settings'].setdefault(self.name, {})
        if 'password' in kw.get(self.name, {}):
            if not kw[self.name]['password']:
                logging.debug('Not updating %r password. No value given.',
                        self.name)
                old_password = session['settings'][self.name].get('password')
                kw[self.name]['password'] = old_password

        # Check if actually changed settings
        old_settings = copy.deepcopy(session['settings'][self.name])
        new_settings = copy.deepcopy(kw.get(self.name))
        # Don't include 'enable' in comparison
        old_settings.pop('enable', None)
        new_settings.pop('enable', None)
        settings_changed = old_settings != new_settings

        session['settings'].update(kw)
        logging.debug('update: session: %r', session)
        try:
            session.get('skip', set()).remove(self.name)
        except KeyError:
            pass
        session.save()

        if settings_changed:
            flash(_('Changes saved'))

        if first_time:
            # Pick the next uncofigured service
            redirect(self.menu.base)
        else:
            redirect(self.url)

    @https()
    @expose()
    @check_settings()
    def clear(self):
        try:
            session.get('skip', set()).remove(self.name)
        except KeyError:
            pass
        session['settings'].pop(self.name, None)
        session.save()
        flash(_('Settings cleared'))
        redirect(self.url)

    @https()
    @expose()
    def skip(self):
        session.setdefault('skip', set())
        session['skip'].add(self.name)
        session.save()
        redirect(self.menu.base)
