from django.conf.urls import patterns, url, include

from django.contrib import admin

from django.views.generic import ListView

from models import Dummy


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Dummy)),
    url(r'^', include('favorites.urls', app_name='favorites', namespace="favorites")),
    url(r'^admin/', include(admin.site.urls)),
)
