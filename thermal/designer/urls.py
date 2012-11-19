from django.conf.urls.defaults import patterns, url

from .views import IndexView
from .views import ParameterEditView
from .views import ResourceEditView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^parameter/$', ParameterEditView.as_view(), name='parameter'),
    url(r'^resource/$', ResourceEditView.as_view(), name='resource'),
)
