from django.conf.urls import *

urlpatterns = patterns('',
    (r'^/about$', 'myproject.nadc.views.About'),
    (r'^/coverage$', 'myproject.nadc.views.Coverage'),
    (r'^/search$', 'myproject.nadc.views.Search'),
    (r'^/(?P<entity>[a-zA-Z0-9_.-]+)/[a-zA-Z0-9_.-]+$', 'myproject.nadc.views.Entity'),
    (r'^', 'myproject.nadc.views.Main'),
    )
