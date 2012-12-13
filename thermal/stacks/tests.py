# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import uuid
import httplib2
import tempfile

from collections import OrderedDict

from django.test.client import MULTIPART_CONTENT
from django import http
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict

from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test
from openstack_dashboard.test.test_data.utils import TestDataContainer

from heatclient import exc

from thermal import api as t_api

INDEX_URL = reverse('horizon:thermal:stacks:index')
LAUNCH_URL = reverse('horizon:thermal:stacks:launch')
UPLOAD_URL = reverse('horizon:thermal:stacks:upload')


class Stack(object):
    def __init__(self, stack_name):
        self.id = uuid.uuid4().get_hex()
        self.stack_name = stack_name


class Event(object):
    def __init__(self, physical_resource_id=None):
        self.id = uuid.uuid4().get_hex()
        self.physical_resource_id = physical_resource_id


class StackViewTest(test.BaseAdminViewTests):
    @test.create_stubs({t_api.heat: ('stacks_list',)})
    def test_index(self):
        stacks = TestDataContainer()
        stacks.add(Stack('test'))
        t_api.heat.stacks_list(IsA(http.HttpRequest)).AndReturn(stacks.list())
        self.mox.ReplayAll()

        res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(res, 'thermal/stacks/index.html')
        stacks_table = res.context['table'].data
        self.assertItemsEqual(stacks_table, stacks.list())

    def test_upload_file(self):
        # create a tempfile
        t = tempfile.NamedTemporaryFile()
        # write some empty json content so parsing succeeds
        t.write('{}')
        t.flush()
        # now open the temp file as a proper file object
        # the tempfile isn't complete enough for django to
        # recognize it as an uploaded file object
        f = open(t.name, 'r')

        # https://docs.djangoproject.com/en/dev/topics/testing/
        res = self.client.post(UPLOAD_URL, {'name': 'test', 'upload_template': f})
        self.assertRedirectsNoFollow(res, LAUNCH_URL)
        # cleanup our file handlers
        f.close()
        t.close()

    @test.create_stubs({httplib2.Http: ('request',)})
    def test_upload_url(self):
        httplib2.Http.request('http://example.com', 'GET').AndReturn(
                              (httplib2.Response({}), ''))
        self.mox.ReplayAll()

        res = self.client.post(UPLOAD_URL, {'http_url': 'http://example.com'})
        self.assertRedirectsNoFollow(res, LAUNCH_URL)

    @test.create_stubs({httplib2.Http: ('request',)})
    def test_upload_url_404(self):
        httplib2.Http.request('http://example.com', 'GET').AndReturn(
                              (httplib2.Response({'status': 404,
                                                  'reason': 'Not Found'}), ''))
        self.mox.ReplayAll()

        res = self.client.post(UPLOAD_URL, {'http_url': 'http://example.com'})
        self.assertTemplateUsed(res, 'thermal/stacks/upload.html')

    @test.create_stubs({cache: ('get',)})
    def test_upload_neither_url_or_file(self):
        res = self.client.post(UPLOAD_URL)
        self.assertTemplateUsed(res, 'thermal/stacks/upload.html')

    @test.create_stubs({cache: ('get',)})
    def test_launch(self):
        t_json = '''{
  "Parameters" : {

    "KeyName" : {
      "Description" : "Name of an existing EC2 KeyPair to enable SSH access to the instances",
      "Type" : "String"
    },

    "LinuxDistribution": {
      "Default": "F17",
      "Description" : "Distribution of choice",
      "Type": "String",
      "AllowedValues" : [ "F16", "F17", "U10", "RHEL-6.1", "RHEL-6.2", "RHEL-6.3" ]
    }
  }
}'''
        cache.get('heat_template_test_user').AndReturn(t_json)
        cache.get('heat_template_name_test_user').AndReturn('test_template')
        
        self.mox.ReplayAll()

        res = self.client.get(LAUNCH_URL)
        self.assertTemplateUsed(res, 'thermal/stacks/launch.html')

    @test.create_stubs({cache: ('get',)})
    def test_launch_redirect(self):
        cache.get('heat_template_test_user').AndReturn(None)
        cache.get('heat_template_name_test_user').AndReturn(None)
        cache.get('heat_template_test_user').AndReturn(None)
        cache.get('heat_template_name_test_user').AndReturn(None)
        
        self.mox.ReplayAll()

        res = self.client.get(LAUNCH_URL)
        self.assertRedirectsNoFollow(res, UPLOAD_URL)
        res = self.client.get(LAUNCH_URL, {}, HTTP_REFERER=INDEX_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @test.create_stubs({cache: ('get',)})
    def test_launch_post_invalid_form(self):
        cache.get('heat_template_test_user').AndReturn('{}')
        cache.get('heat_template_name_test_user').AndReturn('invalid_form')
        
        self.mox.ReplayAll()

        res = self.client.post(LAUNCH_URL)
        self.assertTemplateUsed(res, 'thermal/stacks/launch.html')

    @test.create_stubs({cache: ('get',)})
    def test_launch_post_no_template(self):
        cache.get('heat_template_test_user').AndReturn(None)
        cache.get('heat_template_name_test_user').AndReturn(None)
        cache.get('heat_template_test_user').AndReturn(None)
        cache.get('heat_template_name_test_user').AndReturn(None)
        
        self.mox.ReplayAll()

        res = self.client.post(LAUNCH_URL)
        self.assertRedirectsNoFollow(res, UPLOAD_URL)
        res = self.client.post(LAUNCH_URL, {}, HTTP_REFERER=INDEX_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @test.create_stubs({cache: ('get',),
                        t_api.heat: ('stacks_create',)})
    def test_launch_post_valid_form(self):
        cache.get('heat_template_test_user').AndReturn('{}')
        cache.get('heat_template_name_test_user').AndReturn('{}')
        t_api.heat.stacks_create(IsA(http.HttpRequest),
                                 {'parameters': {},
                                  'stack_name': 'test_launch',
                                  'template': OrderedDict()}
                                ).AndReturn(None)
        self.mox.ReplayAll()

        res = self.client.post(LAUNCH_URL, {'stack_name': 'test_launch'})
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @test.create_stubs({cache: ('get',),
                        t_api.heat: ('stacks_create',)})
    def test_launch_post_valid_form_but_exception(self):
        cache.get('heat_template_test_user').AndReturn('{}')
        cache.get('heat_template_name_test_user').AndReturn('{}')
        t_api.heat.stacks_create(IsA(http.HttpRequest),
                                 {'stack_name': 'test_launch',}
                                ).AndReturn(None)
        self.mox.ReplayAll()

        res = self.client.post(LAUNCH_URL, {'stack_name': 'test_launch'})
        self.assertTemplateUsed(res, 'thermal/stacks/launch.html')

    @test.create_stubs({t_api.heat: ('stacks_get',)})
    def test_detail(self):
        stack = Stack('test')
        t_api.heat.stacks_get(IsA(http.HttpRequest), stack.stack_name).AndReturn(stack)
        self.mox.ReplayAll()

        res = self.client.get(reverse('horizon:thermal:stacks:detail', args=('test',)))
        self.assertTemplateUsed(res, 'thermal/stacks/detail.html')
        self.assertTemplateUsed(res, 'thermal/stacks/_detail_overview.html')

    @test.create_stubs({t_api.heat: ('stacks_get',)})
    def test_detail_w_execption(self):
        stack = Stack('test')
        t_api.heat.stacks_get(IsA(http.HttpRequest), stack.stack_name).AndRaise(Exception)
        self.mox.ReplayAll()

        url = reverse('horizon:thermal:stacks:detail', args=('test',))
        res = self.client.get(url)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @test.create_stubs({t_api.heat: ('stacks_get', 'events_list')})
    def test_events_empty(self):
        stack = Stack('test')
        t_api.heat.stacks_get(IsA(http.HttpRequest), stack.stack_name).AndReturn(stack)
        t_api.heat.events_list(IsA(http.HttpRequest), stack.stack_name).AndReturn([])
        self.mox.ReplayAll()

        url = '%s?tab=stack_details__events' % \
                reverse('horizon:thermal:stacks:detail', args=('test',))
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'thermal/stacks/detail.html')
        self.assertTemplateUsed(res, 'thermal/stacks/_detail_events.html')

    @test.create_stubs({t_api.heat: ('stacks_get', 'events_list')})
    def test_events_non_empty(self):
        stack = Stack('test')
        events = [Event(), Event('test_event')]
        t_api.heat.stacks_get(IsA(http.HttpRequest), stack.stack_name).AndReturn(stack)
        t_api.heat.events_list(IsA(http.HttpRequest), stack.stack_name).AndReturn(events)
        self.mox.ReplayAll()

        url = '%s?tab=stack_details__events' % \
                reverse('horizon:thermal:stacks:detail', args=('test',))
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'thermal/stacks/detail.html')
        self.assertTemplateUsed(res, 'thermal/stacks/_detail_events.html')

    @test.create_stubs({t_api.heat: ('stacks_get', 'events_list')})
    def test_events_w_exception(self):
        stack = Stack('test')
        t_api.heat.stacks_get(IsA(http.HttpRequest), stack.stack_name).AndReturn(stack)
        #t_api.heat.events_list(IsA(http.HttpRequest), stack.stack_name).AndRaise(Exception)
        self.mox.ReplayAll()

        url = '%s?tab=stack_details__events' % \
                reverse('horizon:thermal:stacks:detail', args=('test',))
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'thermal/stacks/detail.html')
        self.assertTemplateUsed(res, 'thermal/stacks/_detail_events.html')

    @test.create_stubs({t_api.heat: ('stacks_list', 'stacks_delete')})
    def test_delete_stack(self):
        stacks = TestDataContainer()
        stacks.add(Stack('delete_me'))
        stack = stacks.first()
        t_api.heat.stacks_list(IsA(http.HttpRequest)).AndReturn(stacks.list())
        t_api.heat.stacks_delete(IsA(http.HttpRequest), stack.id)
        self.mox.ReplayAll()

        formData = {'action': 'stacks__delete__%s' % stack.id}
        res = self.client.post(INDEX_URL, formData)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @test.create_stubs({t_api.heat: ('stacks_get',)})
    def test_ajax_loading_stack(self):
        stack = Stack('update_me')
        t_api.heat.stacks_get(IsA(http.HttpRequest), stack.id).AndReturn(stack)
        self.mox.ReplayAll()

        url = INDEX_URL + "?action=row_update&table=stacks&obj_id=" + stack.id

        res = self.client.get(url, {},
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(res, "horizon/common/_data_table_row.html")

        self.assertContains(res, "update_me", 1, 200)

    @test.create_stubs({t_api.heat: ('stacks_get',)})
    def test_ajax_loading_stack_404(self):
        stack = Stack('update_me')
        t_api.heat.stacks_get(IsA(http.HttpRequest), stack.id).AndRaise(exc.HTTPNotFound)
        self.mox.ReplayAll()

        url = INDEX_URL + "?action=row_update&table=stacks&obj_id=" + stack.id

        res = self.client.get(url, {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(res, "404.html")

    @test.create_stubs({t_api.heat: ('stacks_get',)})
    def test_ajax_loading_stack_w_exception(self):
        stack = Stack('update_me')
        t_api.heat.stacks_get(IsA(http.HttpRequest), stack.id).AndRaise(Exception)
        self.mox.ReplayAll()

        url = INDEX_URL + "?action=row_update&table=stacks&obj_id=" + stack.id

        res = self.client.get(url, {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(res, "404.html")
