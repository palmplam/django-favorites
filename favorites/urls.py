from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from views import *

urlpatterns = patterns("",
    url(r'^add$', ajax_add_favorite, name="favorite_ajax_add"),
    url(r'^remove$', ajax_remove_favorite, name="favorite_ajax_remove"),
    url(r'^delete/(?P<object_id>\d+)/$', drop_favorite, name="favorite_drop"),
    url(r'^toggle/(?P<content_type_id\d+)/(?P<object_id>\d+)/$',
            toggle_favorite, name="favorite_toggle"),
)
