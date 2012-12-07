import os
import logging
import json

from django.conf import settings
from heatclient import client as heat_client
try:
    from openstack_dashboard.api.base import url_for
except:
    from horizon.api.base import url_for

LOG = logging.getLogger(__name__)

### Heat Client ###

def format_parameters(params):
    parameters = {}
    for count, p in enumerate(params, 1):
        parameters['Parameters.member.%d.ParameterKey' % count] = p
        parameters['Parameters.member.%d.ParameterValue' % count] = params[p]
    return parameters

def heatclient(request):
    #TODO: unhardcode api_version
    api_version = "1"
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    endpoint = url_for(request, 'orchestration')
    LOG.debug('heatclient connection created using token "%s" and url "%s"' %
              (request.user.token.id, endpoint))
    kwargs = {
            'token': request.user.token.id,
            'insecure': insecure,
            #'timeout': args.timeout,
            #'ca_file': args.ca_file,
            #'cert_file': args.cert_file,
            #'key_file': args.key_file,
        }
    client = heat_client.Client(api_version, endpoint, **kwargs)
    client.format_parameters = format_parameters
    return client

def stacks_list(request):
    return heatclient(request).stacks.list()

def stacks_create(request, params):
    return heatclient(request).stacks.create(**params)

def stacks_get(request, stack_id):
    return heatclient(request).stacks.get(stack_id)

def stacks_delete(request, stack_id):
    return heatclient(request).stacks.delete(stack_id)

def events_list(request, stack_name):
    return heatclient(request).events.list(stack_name)
