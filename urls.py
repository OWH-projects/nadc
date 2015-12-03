from django.conf.urls import *

urlpatterns = patterns('',
    (r'^/about$', 'myproject.nadc.views.About'),
    (r'^/coverage$', 'myproject.nadc.views.Coverage'),
    (r'^/search', 'myproject.nadc.views.Search'),
    (r'^/(?P<id>[a-zA-Z0-9_.-]+)/[a-zA-Z0-9_.-]+$', 'myproject.nadc.views.EntityPage'),
    (r'^/(?P<govslug>[a-zA-Z0-9_.-]+)$', 'myproject.nadc.views.Govt'),
    (r'^', 'myproject.nadc.views.Main'),
    )
