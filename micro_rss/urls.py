from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'micro_rss.views.home', name='home'),
    
    #below enables app-specific URLs
    url(r'^$', include('reader.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reader/', include('reader.urls')), #duplicates / for now
    url(r'^detail/', include('reader.urls')), #duplicates / for now
    #url(r'^edit/', include('reader.urls')),
)
