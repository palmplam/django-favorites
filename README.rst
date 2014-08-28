================
Django Favorites
================

A generic favorites framework for Django.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "favorites" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'favorites',
    )

2. Include the favorites URLconf in your project urls.py like this::

    url(r'^favorites/', include('favorites.urls')),

3. Run `python manage.py migrate` to create the favorites models.

