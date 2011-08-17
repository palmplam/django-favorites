from django.contrib import admin

from favorites.models import Folder, Favorite


admin.site.register(Folder)
admin.site.register(Favorite)
