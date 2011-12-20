from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'qawa.views.home', name='home'),
    url(r'^auth.json$', 'qawa.views.auth', name='auth'),
    url(r'^register.json$', 'qawa.views.register', name='register'),
    # url(r'^qawa/', include('qawa.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)