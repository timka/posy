"""The base Controller API

Provides the BaseController class for subclassing.
"""
import logging
import tg
import pylons.i18n

from tg import TGController
from tg.exceptions import HTTPException
from tg.controllers import DecoratedController

import formencode.api

log = logging.getLogger(__name__)

# XXX All this stuff is only to fix ToscaWidgets/FormEncode i18n in TG2
# http://trac.turbogears.org/ticket/1999

def set_formencode_translation(languages):
    '''
    Set request specific translation of FormEncode
    '''
    from gettext import translation
    from pylons.i18n import LanguageError
    try:
        t = translation('FormEncode', languages=languages,
                localedir=formencode.api.get_localedir())
    except IOError, ioe:
        raise LanguageError('IOError: %s' % ioe)
    pylons.c.formencode_translation = t


# Idea stolen from Pylons
def pylons_formencode_gettext(value):
    from pylons.i18n import ugettext as pylons_gettext
    from gettext import NullTranslations

    trans = pylons_gettext(value)

    # Translation failed, try formencode
    if trans == value:
        fetrans = pylons.c.formencode_translation
        if not fetrans:
            fetrans = NullTranslations()
        trans = fetrans.ugettext(value)

    return trans


def setup_i18n(languages=None):
    from pylons.i18n import add_fallback, set_lang, LanguageError
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

    def _perform_validate(self, controller, params):
        """
        Validation is stored on the "validation" attribute of the controller's
        decoration.

        If can be in three forms:

        1) A dictionary, with key being the request parameter name, and value a
           FormEncode validator.

        2) A FormEncode Schema object

        3) Any object with a "validate" method that takes a dictionary of the
           request variables.

        Validation can "clean" or otherwise modify the parameters that were
        passed in, not just raise an exception.  Validation exceptions should
        be FormEncode Invalid objects.
        """

        validation = getattr(controller.decoration, 'validation', None)
        if validation is None:
            return params

        # An object used by FormEncode to get translator function
        state = type('state', (),
                {'_': staticmethod(pylons_formencode_gettext)})

        #Initialize new_params -- if it never gets updated just return params
        new_params = {}

        # The validator may be a dictionary, a FormEncode Schema object, or any
        # object with a "validate" method.
        if isinstance(validation.validators, dict):
            # TG developers can pass in a dict of param names and FormEncode
            # validators.  They are applied one by one and builds up a new set
            # of validated params.

            errors = {}
            for field, validator in validation.validators.iteritems():
                try:
                    new_params[field] = validator.to_python(params.get(field),
                            state)
                # catch individual validation errors into the errors dictionary
                except formencode.api.Invalid, inv:
                    errors[field] = inv

            # Parameters that don't have validators are returned verbatim
            for param, param_value in params.items():
                if not param in new_params:
                    new_params[param] = param_value

            # If there are errors, create a compound validation error based on
            # the errors dictionary, and raise it as an exception
            if errors:
                raise formencode.api.Invalid(
                    formencode.schema.format_compound_error(errors),
                    params, None, error_dict=errors)

        elif isinstance(validation.validators, formencode.Schema):
            # A FormEncode Schema object - to_python converts the incoming
            # parameters to sanitized Python values
            new_params = validation.validators.to_python(params, state)

        elif hasattr(validation.validators, 'validate'):
            # An object with a "validate" method - call it with the parameters
            new_params = validation.validators.validate(params, state)

        # Theoretically this should not happen...
        if new_params is None:
            return params

        return new_params

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        
        return TGController.__call__(self, environ, start_response)
