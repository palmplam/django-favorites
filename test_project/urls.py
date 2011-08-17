from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin

from django.views.generic import ListView

from models import Dummy


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Dummy)),
    url(r'^', include('favorites.urls', app_name='favorites', namespace="favorites")),
    url(r'^admin/', include(admin.site.urls)),
)
