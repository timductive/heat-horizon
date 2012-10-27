from django.conf.urls.defaults import patterns, url

from .views import IndexView
from .views import UploadView
from .views import LaunchHeatView
from .views import DetailView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^launch/$', LaunchHeatView.as_view(), name='launch'),
    url(r'^upload/$', UploadView.as_view(), name='upload'),
    url(r'^stack/(?P<stack_name>[^/]+)/$', DetailView.as_view(),
                                           name='detail'),
)
