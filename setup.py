import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'favorites',
    version = '0.3.2',
    description = 'Generic favorites application for Django',
    long_description = read('README.rst'),

    author = 'Djaz Team',
    author_email = 'devweb@liberation.fr',

    packages = find_packages(exclude=['test_project']),
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
