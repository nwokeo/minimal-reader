from django.conf.urls import patterns, url

from reader import views

urlpatterns = patterns('', #ex: /
    url(r'^$', views.index, name='index'), #ex: /reader/
    url(r'^(?P<feed_id_pk>\d+)/$', views.detail, name='detail'), #/reader/[feed_id]
#    url(r'^testing/(?P<article_id_pk>\d+)/$', views.testing, name='testing'), #/reader/testing
    url(r'^update/(?P<feed_id_pk>\d+)/$', views.update, name='update'), #/reader/update/[article_id]
    url(r'^magic$', views.magic, name='magic'),
)
