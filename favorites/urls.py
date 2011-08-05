from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from django.views.generic.list import ListView

from favorites.models import Favorite
from favorites.models import Folder

urlpatterns = patterns("",
                       # favorites urls
                       url(r'^favorites/$',
                           'favorites.views.list_favorites',
                           name='favorites'),

                       # add
                       url(r'^favorite/delete/(?P<app_label>\w+)/(?P<object_name>\w+)/(?P<object_id>\d+)$',
                           'favorites.views.delete_favorite_for_object',
                           name='delete-favorite-for-object'),
                       url(r'^favorite/add/(?P<app_label>\w+)/(?P<object_name>\w+)/(?P<object_id>\d+)$',
                           'favorites.views.create_favorite',
                           name='create-favorite'),

                       # delete
                       url(r'^favorite/delete/(?P<object_id>\d+)$',
                           'favorites.views.delete_favorite',
                           name='delete-favorite'),
                       url(r'^favorite/add/$',
                           'favorites.views.create_favorite',
                           name='create-favorite'),
                       url(r'^favorite/move/(?P<object_id>\d+)$',
                           'favorites.views.move_favorite',
                           name='move-favorite'),

                       # move
                       url(r'^favorite/(?P<favorite_id>\d+)/move/(?P<folder_id>\d+)$',
                           'favorites.views.move_favorite_confirmation',
                           name='move-favorite-confirmation'),

                       # toggle share
                       url(r'^favorite/(?P<favorite_id>\d+)/toggle$',
                           'favorites.views.toggle_share_favorite',
                           name='toggle-share-favorite'),

                       # more listing
                       url(r'^favorite/(?P<app_label>\w+)/(?P<object_name>\w+)/$',
                           'favorites.views.content_type_list',
                           name='content-type-list'),
                       url(r'^favorite/(?P<app_label>\w+)/(?P<object_name>\w+)/folder/(?P<folder_id>\d+)$',
                           'favorites.views.content_type_list',
                           name='content-type-by-folder-list'),

                       # folders urls
                       url('^folders/$',
                           'favorites.views.list_folder',
                           name = 'folders'),
                       url('^folder/add/$',
                           'favorites.views.create_folder',
                           name='create-folder'),
                       url('^folder/delete/(?P<object_id>\d+)$',
                           'favorites.views.delete_folder',
                           name='folder-delete'),
                       url('^folder/update/(?P<object_id>\d+)$',
                           'favorites.views.update_folder',
                           name='update-folder'),
                       )
