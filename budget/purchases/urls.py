from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^/?$', 'purchases.views.purchases'),
    url(r'^add/?$', 'purchases.views.add'),
)
