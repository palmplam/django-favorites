from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from django.views.generic.list import ListView

from favorites.models import Favorite
from favorites.models import Folder

urlpatterns = patterns("",
                       url(r'^favorites/$',
                           ListView.as_view(queryset = Favorite.objects.all())),
                       url(r'^favorite/add/(?P<app_label>\w+)/(?P<object_name>\w+)/(?P<object_id>\d+)$',
                           'favorites.views.create_favorite_confirmation',
                           name='add-to-favorites-confirmation'),
                       url(r'^favorite/add/',
                           'favorites.views.create_favorite',
                           name='create-favorite'),

                       # folders urls
                       url('folders/',
                           'favorites.views.list_folder',
                           name = 'folders'),
                       url('^folder/add/',
                           'favorites.views.create_folder',
                           name='create-folder'),
                       url('^folder/delete/(?P<object_id>\d+)',
                           'favorites.views.delete_folder_confirmation',
                           name='delete-folder-confirmation'),
                       url('^folder/delete/$',
                           'favorites.views.delete_folder',
                           name='delete-folder'),
                       url('^folder/update/(?P<object_id>\d+)',
                           'favorites.views.update_folder',
                           name='update-folder'),
                       )
