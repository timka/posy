from setuptools import setup, find_packages

setup(
    name='posy',
    version='0.1',
    description=('Crossposter library for multiple (mirco-)blogs'
                 ' and social networks'),
    license='http://www.apache.org/licenses/LICENSE-2.0',
    author='Timur Izhbulatov',
    author_email='timochka@gmail.com',
    url='http://code.google.com/p/posy/',
    install_requires=[
        'simplejson',
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    #test_suite='nose.collector',

    entry_points="""
    [posy.services]
    twitter = posy.services.twitter:Twitter
    plurk = posy.services.plurk:Plurk
    lj = posy.services.lj:LJ
    """,
    zip_safe=False,
)
