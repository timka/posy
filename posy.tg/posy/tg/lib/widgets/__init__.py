
# - * - coding: utf-8 - * -
# TODO: Move JS and templates to separate files
import logging
import tw.api
import tw.forms
import formencode.validators as validators
from tw.api import lazystring as _

from posy.api import Posy

languages = [
    ('en', 'English'),
    ('ru', unicode('Русский', 'utf-8')),
]

functions = tw.api.JSSource('''
var posyOnSubmit = function(form) {

    var zeropadding = function(n) {
        return n > 9 ? n : '0' + n;
    }
    var zp = zeropadding;

    var now = new Date();
    var year = now.getFullYear(); 
    var month = zp(now.getMonth() + 1);
    var day = zp(now.getDate());
    var h = zp(now.getHours());
    var m = zp(now.getMinutes());
    var s = zp(now.getSeconds());
    var timestamp = year + '-' + month + '-' + day + 'T';
    timestamp += h + ':' + m + ':' + s;
    if (form.timestamp) {
        form.timestamp.value = timestamp; 
    }
}

var focusElement = function(id) {
    var element = document.getElementById(id);
    if (element) {
        element.focus();
        //element.select();
    }
}

var setSubmitOnChange = function(id) {
    if (!id) {
        return;
    }
    document.getElementById(id).onchange = function(event) {
        var form = document.getElementById(id).form;
        form.submit();
    }
}

var setClearOnClick = function(id, url) {
    if (!id || !url) {
        return;
    }
    document.getElementById(id).onclick = function(event) {
        window.location = url;
    }
}

var setClearAllOnClick = function(id, url, message) {
    if (!id || !url || !message) {
        return;
    }
    document.getElementById(id).onclick = function(event) {
        if (!confirm(message)) {
            return;
        }
        window.location = url;
    }
}

var setOnKeyUp = function(id, checkBoxId) {
    var element = document.getElementById(id);
    //alert(element);
    if (!element) {
        return;
    }
    element.onkeyup = function(event) {
        //alert(event);
        if (!element.value) {
            return;
        }

        var checkbox = document.getElementById(checkBoxId);
        //alert(checkbox);
        if (!checkbox) {
            return;
        }

        checkbox.onchange = null;
        checkbox.checked = true;
    }
}

var setSkipOnClick = function(id, url) {
    if (!id || !url) {
        return;
    }
    document.getElementById(id).onclick = function(event) {
        window.location = url;
    }
}
''')


focusElement = tw.api.js_function('focusElement')

class LanguageSelect(tw.forms.SingleSelectField):
    validator = None
    label_text = _('Language')
    help_text = _('Application language'),
    options = languages
    is_required = False

    def update_params(self, d):
        super(LanguageSelect, self).update_params(d)
        self.add_call(tw.api.js_function('setSubmitOnChange')(self.id, None))


class LangSelectForm(tw.forms.Form):
    validator = None
    javascript = [functions]
    submit_text = None
    method = 'GET'
    is_required = False

    class fields(tw.api.WidgetsList):
        lang = LanguageSelect()
    
    def display(self, value=None, **kw):
        #logging.debug('display: %s', locals())
        return super(LangSelectForm, self).display(value, **kw)

    def validate(self, value, state=None):
        #logging.debug('validate: %s', locals())
        return super(LangSelectForm, self).validate(value, state)

    def update_params(self, d):
#        import traceback
#        logging.debug(''.join(traceback.format_stack()))
#        logging.debug('update_params: %s', locals())
        return super(LangSelectForm, self).update_params(d)


class PosySubmitButton(tw.forms.SubmitButton):
    css_class = 'submit-button'
    suppress_label = True
    attrs = {
        'accesskey': 'S',
        'title': _('Press Alt+Shift+S to submit form'),
        'value': _('Send!'),
    }


class Content(tw.forms.TextArea):
    css_class = 'content-text'
    suppress_label = True


class PosyForm(tw.forms.ListForm):
    attrs = dict(onsubmit='posyOnSubmit(this)')
    javascript = [functions]
    is_required = False
    css_classes = ['posyform', 'listform']

    class fields(tw.api.WidgetsList):
        content = Content(validator=validators.String(not_empty=True,
            max=1024 * 4))
        timestamp = tw.forms.HiddenField(
                validator=tw.forms.validators.DateTimeConverter(
                    format='%Y-%m-%dT%H:%M:%S',
                    not_empty=True))
        submit = PosySubmitButton()

    def update_params(self, d):
        super(PosyForm, self).update_params(d)
        self.add_call(focusElement(self.c.content))


class SettingsFieldSet(tw.forms.TableFieldSet):
    css_class = 'settings'
    suppress_label = True
    legend = False
    hover_help = True


class ServiceSettings(SettingsFieldSet):
    class fields(tw.api.WidgetsList):
        username = tw.forms.TextField(label_text=_('Username'),
                help_text=_("Your account's username for this service"),
                validator=validators.String(not_empty=True))
        password = tw.forms.PasswordField(label_text=_('Password'),
                help_text=_('Posy does not fill password fields on web pages'
                    " for security reasons. This field will be applied only"
                    " if not empty value is entered."
                    " Use your browser's password manager, if you"
                    " want this field to be filled automatically."),
                validator=validators.String())
        enable = tw.forms.CheckBox(label_text=_('Enable'),
                help_text=_('Enable sending messages to this service'))

    def update_params(self, d):
        super(ServiceSettings, self).update_params(d)

        password = self.c.password
        username = self.c.username
        enable = self.c.enable

        enable.add_call(tw.api.js_function('setSubmitOnChange')(enable.id))
        setOnKeyUp = tw.api.js_function('setOnKeyUp')
        password.add_call(setOnKeyUp(password.id, enable.id))
        username.add_call(setOnKeyUp(username.id, enable.id))


class GeneralSettings(SettingsFieldSet):
    legend = _('General')

    class fields(tw.api.WidgetsList):
        email = tw.forms.TextField(
            label_text=_('Email (optional)'),
            help_text=_('Optional email for sending debugging output.'
                ' Fill this field if you wish to receive weird emails :)'),
            validator=validators.Email())
        # shorten_urls = tw.forms.CheckBox(
        #         label_text=_("Shorten URL's automatically"))


class Button(tw.forms.Button):
    type = 'button'
    text = 'Button'

    title = None
    accesskey = None
    url = None

    params = ['url', 'text', 'type', 'title', 'accesskey']

    suppress_label = True
    is_required = False

    template = '''
<button xmlns="http://www.w3.org/1999/xhtml"
    xmlns:py="http://genshi.edgewall.org/"
    id="${id}"
    class="${css_class}"
    type="${type}"
    title="${title}"
    py:attrs="attrs">${text}</button>
'''


class ClearSettings(Button):
    text = _('Clear Settings')
    title = _('Press Alt+Shift+C to clear settings on this page')
    accesskey = 'C'

    css_class = 'clear-settings'

    def update_params(self, d):
        super(ClearSettings, self).update_params(d)
        self.add_call(tw.api.js_function('setClearOnClick')(self.id, d['url']))


class ApplySettings(Button):
    type = 'submit'
    text = _('Apply'),
    accesskey = 'A'
    title = _('Press Alt+Shift+A to apply settings')


class ClearAllSettings(Button):
    text = _('Clear All Settings')
    attrs = dict(title=_('Clear general and all service settings'))
    message = _('Really clear ALL settings?')
    params = ['message', 'url']

    css_class = 'clear-all-settings'

    def update_params(self, d, **kw):
        #logging.debug('ClearAllSettings: update_params: locals: %s', locals())
        super(ClearAllSettings, self).update_params(d, **kw)
        setClearAllOnClick = tw.api.js_function('setClearAllOnClick')
        # XXX: lazystring cannot be serialized to JSON, so converting to
        # plain unicode
        message = unicode(str(self.message), 'utf-8')
        self.add_call(setClearAllOnClick(self.id, d['url'], message))


class SettingsForm(tw.forms.ListForm):
    submit_text = None
    show_children_errors = False
    name = 'settings'
    css_classes = ['settingsform', 'listform']
    javascript = [functions]

    def update_params(self, d, **kw):
        #logging.debug('SettingsForm.update_params: %s', locals())
        super(SettingsForm, self).update_params(d, **kw)
        if d.error:
            return
        # Focus 1st input field
        matched = list(self.walk(lambda x: isinstance(x, tw.forms.InputField)))
        if matched:
            self.add_call(focusElement(matched[0]))


class SkipButton(Button):
    text = _('Skip')
    title = _('Go to next unconfigured service')

    def update_params(self, d):
        super(SkipButton, self).update_params(d)
        setSkipOnClick = tw.api.js_function('setSkipOnClick')
        self.add_call(setSkipOnClick(self.id, d['url']))


class Buttons(tw.forms.ContainerMixin, tw.forms.FormField):
    validator = None
    is_required = False
    suppress_label = True
    #strip_name = True

    template = '''<div xmlns="http://www.w3.org/1999/xhtml" 
          xmlns:py="http://genshi.edgewall.org/"
          id="${id}"
          class="${css_class}"
          py:attrs="attrs">
    <span py:for="field in fields"
        id="${field.id}_container"
        py:attrs="args_for(field).get('container_attrs') or field.container_attrs">
        ${field.display(value_for(field), **args_for(field))}
    </span>
</div>
'''

    class fields(tw.api.WidgetsList):
        clear = ClearSettings()
        submit = ApplySettings()
        skip = SkipButton()

    def update_params(self, d, **kw):
        #logging.debug('Buttons.update_params: %s', locals())
        super(Buttons, self).update_params(d, **kw)


class GeneralSettingsButtons(Buttons):
    class fields(tw.api.WidgetsList):
        clear = ClearSettings()
        submit = ApplySettings()
        clear_all = ClearAllSettings()


class GeneralSettingsForm(SettingsForm):
    class fields(tw.api.WidgetsList):
        general = GeneralSettings()
        buttons = GeneralSettingsButtons()


settings_forms = dict(
    (
        name,
        SettingsForm('settings',
            fields=[
                ServiceSettings(id=name, legend=service.display_name),
                #ClearSettings('clear'),
                #ApplySettings('submit'),
                Buttons('buttons'),
            ]
        )
    )
    for name, service in list(Posy())
)
settings_forms['general'] = GeneralSettingsForm('general_settings')

posy_form = PosyForm('posyform')
langform = LangSelectForm('langform')
