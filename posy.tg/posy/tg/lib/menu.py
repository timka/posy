import tg
from tg import session
from pylons.i18n import lazy_ugettext

from posy.api import retrieve_services as posy_services
from posy.tg.lib import util


class Menu(list):
    '''
    List of (name, item) pairs where items are accessible by names
    '''
    #Implementation is limited to what will be actually used

    __instance__ = None
    base = None

    def __init__(self, menu=[]):
        if not menu:
            base = self.base
            make_controller = self.make_controller

            def make_item(make_controller, base, name, display_name,
                    item_class=MenuItem):
                return name, item_class(make_controller, base, name,
                        display_name)

            menu = [ make_item(make_controller, base, name, value.display_name)
                     for name, value in sorted(posy_services()) ]

            menu.append(make_item(make_controller, base, 'general',
                lazy_ugettext('General'),
                GeneralSettingsItem))

        super(Menu, self).__init__(menu)

    def __getitem__(self, name):
        if isinstance(name, basestring):
            return dict(self)[name]
        return super(Menu, self).__getitem__(name)

    @classmethod
    def make_controller(cls, name):
        '''
        Get controller by name
        '''
        raise NotImplenentedError('make_controller')


class BaseMenuItem(tuple):
    # Need signature other than tuple's __new__
    def __new__(cls, controller_class, base, name, display_name):
        return super(BaseMenuItem, cls).__new__(cls, (name, display_name))

    def __init__(self, make_controller, base, name, display_name):
        self.make_controller = make_controller
        self.base = base
        self.name = name
        self.display_name = display_name

    @property
    def controller(self):
        return self.make_controller(self.name)

    @property
    def url(self):
        return tg.url(util.path_join(self.base, self.name))

    @property
    def is_new(self):
        new_settings = 'settings' not in session
        settings = session.get('settings', {})
        return self.name not in settings or new_settings


class MenuItem(BaseMenuItem):
    @property
    def is_configured(self):
        settings = session.get('settings', {})
        return bool(settings.get(self.name, {}).get('password'))

    @property
    def is_enabled(self):
        settings = session.get('settings', {})
        return settings.get(self.name, {}).get('enable') or self.is_new


class GeneralSettingsItem(BaseMenuItem):
    @property
    def is_configured(self):
        settings = session.get('settings', {})
        return bool(settings.get(self.name, {}).get('email'))

    @property
    def is_enabled(self):
        return True
