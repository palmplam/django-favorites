from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns
from django.views.generic.list import ListView

from favorites.models import Favorite
from favorites.models import Folder


urlpatterns = patterns("",
                       # favorites urls
                       url(r'^favorites/$',
                           'favorites.views.favorite_list',
                           name='favorite_list'),
                       # add
                       url(r'^favorite/add/(?P<app_label>\w+)/(?P<object_name>\w+)/(?P<object_id>\d+)$',
                           'favorites.views.favorite_add',
                           name='favorite_add'),
                       # delete
                       url(r'^favorite/delete/(?P<object_id>\d+)$',
                           'favorites.views.favorite_delete',
                           name='favorite_delete'),
                       # delete for object
                       url(r'^favorite/delete/(?P<app_label>\w+)/(?P<object_name>\w+)/(?P<object_id>\d+)$',
                           'favorites.views.favorite_delete_for_object',
                           name='favorite_delete_for_object'),
                       # move
                       url(r'^favorite/move/(?P<object_id>\d+)$',
                           'favorites.views.favorite_move',
                           name='favorite_move'),
                       # move
                       url(r'^favorite/(?P<favorite_id>\d+)/move/(?P<folder_id>\d*)$',
                           'favorites.views.favorite_move_to_folder',
                           name='favorite_move_to_folder'),
                       # toggle share
                       url(r'^favorite/(?P<favorite_id>\d+)/toggle$',
                           'favorites.views.favorite_toggle_share',
                           name='favorite_toggle_share'),
                       # more listing
                       url(r'^favorite/(?P<app_label>\w+)/(?P<object_name>\w+)/$',
                           'favorites.views.favorite_content_type_and_folder_list',
                           name='favorite_content_type_list'),
                       url(r'^favorite/(?P<app_label>\w+)/(?P<object_name>\w+)/folder/(?P<folder_id>\d+)$',
                           'favorites.views.favorite_content_type_and_folder_list',
                           name='favorite_content_type_and_folder_list'),
                       # folders urls
                       url('^folders/$',
                           'favorites.views.folder_list',
                           name = 'folder_list'),
                       url('^folder/add/$',
                           'favorites.views.folder_add',
                           name='folder_add'),
                       url('^folder/delete/(?P<object_id>\d+)$',
                           'favorites.views.folder_delete',
                           name='folder_delete'),
                       url('^folder/update/(?P<object_id>\d+)$',
                           'favorites.views.folder_update',
                           name='folder_update'),
                       )
