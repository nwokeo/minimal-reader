from django.conf.urls import patterns, url

from reader import views

urlpatterns = patterns('', #ex: /
    url(r'^$', views.index, name='index'), #ex: /reader/
    url(r'^(?P<feed_id_pk>\d+)/$', views.detail, name='detail'), #/reader/[feed_id]
    #url(r'^update/(?P<feed_id_pk>\d+)/$', views.update, name='update'), #/reader/update/[article_id]
    url(r'^magic$', views.magic, name='magic'),
    url(r'^allread/(?P<feed_id_pk>\d+)/$', views.allread, name='allread'), #/reader/allread/[feed_id]
    url(r'^update/$', views.update, name='update'),
    #url(r'^edit/(?P<feed_id_pk>\d+)/$', views.edit, name='edit'), #/reader/edit/[feed_id]
    #url(r'^edit/update/$', views.edit_update, name='edit_update'), #/reader/edit/update/[feed_id]
    #url(r'^edit_label$', views.edit_label, name='edit_label'),
)
