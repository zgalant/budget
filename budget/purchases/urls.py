from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^/?$', 'purchases.views.purchases'),
    url(r'^add/?$', 'purchases.views.add'),
    url(r'^delete/(?P<id>[0-9]+)?$', 'purchases.views.delete'),
    url(r'^edit/(?P<id>[0-9]+)?$', 'purchases.views.edit'),
    url(r'^sync/?$', 'purchases.views.sync_tags'),
)
