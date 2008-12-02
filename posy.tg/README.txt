About
=====

``posy.tg`` is a part of Posy project — a crossposter for multiple
(micro-)blogging services and platforms.

The ``posy.tg`` component is TurboGears 2 web application which aims to provide
a UI for Posy crossposter library.

Installation and Setup
======================

Install ``posy.tg`` using easy_install::

    easy_install posy.tg

Make a config file as follows::

    paster make-config posy.tg config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.
