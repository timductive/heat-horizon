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
        httplib2.Http.request(CATALOGUES[key]['feed'], 'GET').AndReturn(
                              (httplib2.Response({}), '{}'))
        self.mox.ReplayAll()

        res = self.client.get('%s?catalogue=%s' % (
            reverse('horizon:thermal:catalogues:index'), key))
        self.assertTemplateUsed(res, 'thermal/catalogues/index.html')

    @test.create_stubs({httplib2.Http: ('request',)})
    def test_index_aws(self):
        key = 'aws-cloudformation-templates-us-east-1'
        content = '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/"/>'
        httplib2.Http.request(CATALOGUES[key]['feed'], 'GET').AndReturn(
                              (httplib2.Response({}), content))
        self.mox.ReplayAll()

        res = self.client.get('%s?catalogue=%s' % (
            reverse('horizon:thermal:catalogues:index'), key))
        self.assertTemplateUsed(res, 'thermal/catalogues/index.html')
