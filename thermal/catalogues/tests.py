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

from django import http
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict
from django.contrib import sessions

from mox import IsA

from thermal import api as t_api
from thermal import CATALOGUES
from openstack_dashboard import api
from openstack_dashboard.test import helpers as test
from openstack_dashboard.test.test_data.utils import TestDataContainer


class CatalogueViewTest(test.BaseAdminViewTests):
    @test.create_stubs({httplib2.Http: ('request',)})
    def test_index_github(self):
        key = 'github-heatapi-template'
        content = '''[
{
    "type": "file",
    "path": "templates/TestTemplate.template",
    "url": "https://exmaple.com/repos/test/contents/templates/TestTemplate.template",
    "sha": "b7ec6c417b24be908c55ddcbf97d68e7986b2aa6",
    "_links": {
      "html": "https://example.com/test/blob/master/templates/TestTemplate.template",
      "git": "https://example.com/repos/test/blobs/b7ec6c417b24be908c55ddcbf97d68e7986b2aa6",
      "self": "https://example.com/repos/test//contents/templates/TestTemplate.template"
    },
    "html_url": "https://example.com/test/blob/master/templates/TestTemplate.template",
    "size": 9984,
    "name": "TestTemplate.template",
    "git_url": "https://example.com/repos/test/git/blobs/b7ec6c417b24be908c55ddcbf97d68e7986b2aa6"
  }
]'''
        httplib2.Http.request(CATALOGUES[key]['feed'], 'GET').AndReturn(
                              (httplib2.Response({}), content))
        self.mox.ReplayAll()

        res = self.client.get('%s?catalogue=%s' % (
            reverse('horizon:thermal:catalogues:index'), key))
        self.assertTemplateUsed(res, 'thermal/catalogues/index.html')

    @test.create_stubs({httplib2.Http: ('request',)})
    def test_index_github_error(self):
        key = 'github-heatapi-template'
        httplib2.Http.request(CATALOGUES[key]['feed'], 'GET').AndReturn(
                              (httplib2.Response({}), '{"message": "error"}'))
        self.mox.ReplayAll()

        res = self.client.get('%s?catalogue=%s' % (
            reverse('horizon:thermal:catalogues:index'), key))
        self.assertTemplateUsed(res, 'thermal/catalogues/index.html')

    @test.create_stubs({httplib2.Http: ('request',)})
    def test_index_aws(self):
        key = 'aws-cloudformation-templates-us-east-1'

        content = '''<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Name>cloudformation-templates-us-east-1</Name>
  <Prefix/>
  <Marker/>
  <MaxKeys>1000</MaxKeys>
  <IsTruncated>false</IsTruncated>
  <Contents>
    <Key>TestTemplate.template</Key>
    <LastModified>2012-03-20T04:50:24.000Z</LastModified>
    <ETag>"18b4ee64c6d448796a5b69e566c2767e"</ETag>
    <Size>5061</Size>
    <StorageClass>STANDARD</StorageClass>
  </Contents>
</ListBucketResult>'''
        httplib2.Http.request(CATALOGUES[key]['feed'], 'GET').AndReturn(
                              (httplib2.Response({}), content))
        self.mox.ReplayAll()

        res = self.client.get('%s?catalogue=%s' % (
            reverse('horizon:thermal:catalogues:index'), key))
        self.assertTemplateUsed(res, 'thermal/catalogues/index.html')

    @test.create_stubs({httplib2.Http: ('request',),})
                        #sessions: ('get',)})
    def test_getting_template_from_catalogue(self):
        #sessions.get('catalogue').AnReturn({}) 
        session = self.client.session
        session['catalogue'] = 'cat_id'
        self.mox.ReplayAll()

        res = self.client.post(
            reverse('horizon:thermal:catalogues:index'),
            {'blah': 'TestTemplate.template'})
        self.assertTemplateUsed(res, 'thermal/catalogues/index.html')
