try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='posy.tg',
    version='0.2',
    author='Timur Izhbulatov',
    author_email='timochka@gmail.com',
    description=('Crossposter application for multiple (mirco-)blogs'
                 ' and social networks'),
    license='http://www.apache.org/licenses/LICENSE-2.0',
    url='http://code.google.com/p/posy/',
    install_requires=[
        # XXX workaround for weird unsatisfiable zope.interface requirement
        "zope.interface >= 3.5.1",
        "posy",
        "pycryptopp",
        "TurboGears2",
        "tw.forms",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['webtest', 'beautifulsoup'],
    package_data={'posy.tg': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*',
                                 'public/*/*']},
    message_extractors = {'posy/tg': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},
    
    entry_points="""
    [paste.app_factory]
    main = posy.tg.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
