from django.conf.urls import *

urlpatterns = patterns('',
    (r'^/about$', 'myproject.nadc.views.About'),
    (r'^/coverage$', 'myproject.nadc.views.Coverage'),
    (r'^/search$', 'myproject.nadc.views.Search'),
    (r'^/donor/(?P<donor>[a-zA-Z0-9_.-]+)$', 'myproject.nadc.views.Donor'),
    (r'^/recipient/(?P<recipient>[a-zA-Z0-9_.-]+)$', 'myproject.nadc.views.Recipient'),
    (r'^', 'myproject.nadc.views.Main'),
    )