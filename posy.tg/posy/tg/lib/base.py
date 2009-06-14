"""The base Controller API

Provides the BaseController class for subclassing.
"""
import logging
import tg
import pylons

from tg import TGController
from tg.exceptions import HTTPException
from tg.controllers import DecoratedController
from tg.i18n import set_formencode_translation
from pylons.i18n import add_fallback, set_lang, LanguageError

log = logging.getLogger(__name__)

# XXX All this is to fix http://trac.turbogears.org/ticket/2335

def setup_i18n(languages=None):
    if not languages:
        languages = pylons.request.accept_language.best_matches()
    if languages:
        for lang in languages[:]:
            try:
                add_fallback(lang)
            except LanguageError:
                # if there is no resource bundle for this language
                # remove the language from the list
                languages.remove(lang)
                log.debug("Skip language %s: not supported", lang)
        # if any language is left, set the best match as a default
        if languages:
            try:
                set_lang(languages[0])
            except LanguageError:
                log.debug("Language %s: not supported", languages[0])
            else:
                log.debug("Set request language to %s", languages[0])

            try:
                set_formencode_translation(languages)
            except LanguageError:
                log.debug("Language %s: not supported by FormEncode",
                        languages[0])
            else:
                log.debug("Set request language for FormEncode to %s",
                        languages[0])


class BaseController(TGController):
    """Base class for the root of a web application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.
    """

    def _perform_call(self, func, args):
        languages = []
        lang = tg.session.get('lang')
        if lang:
            languages.append(lang)
        setup_i18n(languages)

        routingArgs = None

        if isinstance(args, dict) and 'url' in args:
            routingArgs = args['url']

        try:
            controller, remainder, params = self._get_routing_info(routingArgs)
            result = DecoratedController._perform_call(
                self, controller, params, remainder=remainder)
        except HTTPException, httpe:
            result = httpe
            # 304 Not Modified's shouldn't have a content-type set
            if result.status_int == 304:
                result.headers.pop('Content-Type', None)
            result._exception = True
        return result
