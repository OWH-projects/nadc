from django.conf.urls import *
from myproject.nadc.views import DonationDetailView

urlpatterns = patterns('',
    (r'^/about$', 'myproject.nadc.views.About'),
    (r'^/coverage$', 'myproject.nadc.views.Coverage'),
    (r'^/datewidget$', 'myproject.nadc.views.DateWidget'),
    (r'^/search', 'myproject.nadc.views.Search'),
    (r'^/api/(?P<startmonth>[0-9_.-]{2})/(?P<startday>[0-9_.-]{2})/(?P<startyear>[0-9_.-]{4})/(?P<endmonth>[0-9_.-]{2})/(?P<endday>[0-9_.-]{2})/(?P<endyear>[0-9_.-]{4})/(?P<type>[a-zA-Z0-9_.-]+)', 'myproject.nadc.views.DateJSON'),
    (r'^/api/(?P<startmonth>[0-9]{2})/(?P<startday>[0-9]{2})/(?P<startyear>[0-9]{4})/(?P<type>[a-zA-Z0-9_.-]+)', 'myproject.nadc.views.DateJSON'),
    (r'^/zip/(?P<zipcode>[0-9]+)$', 'myproject.nadc.views.ZipCode'),
    (r'^/daterange/(?P<startdate>[0-9_.-]{8})/(?P<enddate>[0-9_.-]{8})', 'myproject.nadc.views.DatePage'),
    (r'^/daterange/(?P<startdate>[0-9_.-]{8})', 'myproject.nadc.views.DatePage'),
    (r'^/(?P<id>[a-zA-Z0-9_.-]+)/[a-zA-Z0-9_.-]+$', 'myproject.nadc.views.EntityPage'),
    (r'^/(?P<pk>[0-9]+)$', DonationDetailView.as_view()),
    (r'^/(?P<govslug>[a-zA-Z0-9_.-]+)$', 'myproject.nadc.views.Govt'),
    (r'^', 'myproject.nadc.views.Main'),
    )
