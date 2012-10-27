import os
import logging
import json

from django.conf import settings
from heat import client as heat_client
try:
    from openstack_dashboard.api.base import url_for
except:
    from horizon.api.base import url_for

LOG = logging.getLogger(__name__)

### Heat Client ###


def format_parameters(self, params):
    parameters = {}
    for count, p in enumerate(params, 1):
        parameters['Parameters.member.%d.ParameterKey' % count] = p
        parameters['Parameters.member.%d.ParameterValue' % count] = params[p]
    return parameters

heat_client.HeatClient.format_parameters = format_parameters


def heatclient(request):
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    LOG.debug('heatclient connection created using token "%s" and url "%s"' %
              (request.user.token.id, url_for(request, 'cloudformation')))
    options = {'host': 'localhost',
               'port': 8000,
               'username': request.user.username,
               #'password': request.user.token.id, ###NOPE
               'password': 'verybadpass',
               # TODO: Why is this not tenant_name?
               #'tenant': request.user.tenant_name,
               'tenant': request.user.username,
               'auth_url': settings.OPENSTACK_KEYSTONE_URL,
               #'auth_token': request.user.token.id, ###NOPE
               'auth_token': 'd57638a3cced1564cc0d',
               'region': 'RegionOne',
               'insecure': insecure,
              }
    return heat_client.get_client(**options)
