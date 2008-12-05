import logging
import urlparse

import tg
from pylons.i18n import ugettext as _


class check_settings(object):
    def __call__(self, func):
        def check_settings(func, self, *args, **kwargs):
            if (not tg.session.get('settings')):
                msg = _('You need to set up at least one service before'
                        ' you can use the application.')
                tg.flash(msg)
                tg.redirect(tg.url('/settings'))

        deco = tg.decorators.Decoration.get_decoration(func)
        deco.register_hook('before_validate', check_settings)
        return func


class post_only(object):
    '''
    Makes sure that request method is POST. If it is not, redirects to URL
    specified in `redirect` argument or raises HTTPMethodNotAllowed.
    '''

    def __init__(self, redirect=None):
        self.redirect = redirect 

    def __call__(self, func):
        def check_request_method(*args, **kw):
            if tg.request.method == 'POST':
                return

            if self.redirect:
                tg.redirect(self.redirect)
            else:
                headers = dict(Allow='POST')
                raise tg.exceptions.HTTPMethodNotAllowed(headers=headers)

        deco = tg.decorators.Decoration.get_decoration(func)
        deco.register_hook('before_validate', check_request_method)
        return func


class https(object):
    '''
    Makes sure that request URL's scheme is HTTPS. If it is not, do a redirect.
    '''

    def __init__(self, redirect=None):
        self.redirect = redirect 

    def __call__(self, func):
        if not tg.config.get('posy.tg.redirect_to_https'):
            return func
        def check_request_url_scheme(*args, **kw):
            if tg.request.headers.get('X-Forwarded-Scheme', '').lower() == 'https':
                return
            parsed_url = urlparse.urlparse(tg.request.url)
            new_url = urlparse.urlunparse(('https',) + parsed_url[1:])
            raise tg.exceptions.HTTPFound(location=new_url).exception

        deco = tg.decorators.Decoration.get_decoration(func)
        deco.register_hook('before_validate', check_request_url_scheme)
        return func
