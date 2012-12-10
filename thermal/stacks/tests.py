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

from collections import OrderedDict

from django.test.client import MULTIPART_CONTENT
from django import http
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict

from mox import IsA

from thermal import api as t_api
from openstack_dashboard import api
from openstack_dashboard.test import helpers as test
from openstack_dashboard.test.test_data.utils import TestDataContainer


INDEX_URL = reverse('horizon:thermal:stacks:index')
LAUNCH_URL = reverse('horizon:thermal:stacks:launch')
UPLOAD_URL = reverse('horizon:thermal:stacks:upload')


class Stack(object):
    def __init__(self, stack_name):
        self.id = uuid.uuid4().get_hex()
        self.stack_name = stack_name

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
        #####
        # This test works if you open a file, but not if you construct a
        # temproary file, need to fix this
        #####
        import tempfile
        f = tempfile.NamedTemporaryFile()
        f.write('{}')
        f.flush()
        #f = open('/etc/passwd', 'r')
        self.mox.ReplayAll()

        # https://docs.djangoproject.com/en/dev/topics/testing/
        res = self.client.post(UPLOAD_URL, {'name': 'test', 'upload_template': f})
        self.assertRedirectsNoFollow(res, LAUNCH_URL)

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
        cache.get('heat_template_test_user').AndReturn('{}')
        cache.get('heat_template_name_test_user').AndReturn('{}')
        
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
        cache.get('heat_template_name_test_user').AndReturn('{}')
        
        self.mox.ReplayAll()

        res = self.client.post(LAUNCH_URL)
        self.assertTemplateUsed(res, 'thermal/stacks/launch.html')
        #instances = res.context['table'].data
        #self.assertItemsEqual(instances, servers)

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

    ####
    # These two have errors that need to be figured out.
    # the code gets covered but the template redering fails
    ####

    #@test.create_stubs({t_api.heat: ('stacks_get',)})
    #def test_detail(self):
    #    stack = Stack('test')
    #    t_api.heat.stacks_get(IsA(http.HttpRequest), stack.stack_name).AndReturn(Stack)
    #    self.mox.ReplayAll()

    #    res = self.client.get(reverse('horizon:thermal:stacks:detail', args=('test',)))
    #    self.assertTemplateUsed(res, 'thermal/stacks/detail.html')

    #@test.create_stubs({t_api.heat: ('stacks_get',)})
    #def test_detail_invalid_stack(self):
    #    stack = Stack('test')
    #    t_api.heat.stacks_get(IsA(http.HttpRequest), stack.stack_name).AndRaise(Exception)
    #    self.mox.ReplayAll()

    #    url = reverse('horizon:thermal:stacks:detail', args=('test',))
    #    print url
    #    res = self.client.get(url)
    #    self.assertRedirectsNoFollow(res, INDEX_URL)

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
    def test_ajax_loading_instances(self):
        stack = Stack('update_me')
        t_api.heat.stacks_get(IsA(http.HttpRequest), stack.id).AndReturn(stack)
        self.mox.ReplayAll()

        url = INDEX_URL + "?action=row_update&table=stacks&obj_id=" + stack.id

        res = self.client.get(url, {},
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(res, "horizon/common/_data_table_row.html")

        self.assertContains(res, "update_me", 1, 200)
