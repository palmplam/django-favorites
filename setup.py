from distutils.core import setup
import os


modules = [
    'favorites.templatetags',
    'favorites.templates.favorites',
]


setup(
    name = 'favorites',
    version = '0.1',
    description = 'Generic favorites application for Django',
    author = 'Andrew Gwozdziewycz',
    author_email = 'git@apgwoz.com',
    packages = ['favorites'] + modules,
    include_package_data=True,
    package_data = {
           '': ['*.txt', '*.rst'],
           'favorites': ['templates/favorites/*.html'],
       },
    
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
