import httplib2
import logging

from django.core import urlresolvers
from django.core.cache import cache
from django.utils.http import urlencode
from django.http import Http404
from django.template.defaultfilters import title
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from horizon import tables
from horizon import messages
from horizon.utils.filters import replace_underscores

from thermal import CATALOGUES

LOG = logging.getLogger(__name__)


class LaunchCatalogue(tables.Action):
    name = "launch"
    verbose_name = _("Launch")
    classes = ("btn-create", )#("ajax-modal", "btn-create")


    def _get_template(self, template_name):
        # TODO: make cache dir configurable via django settings
        # TODO: make disabling ssl verification configurable too
        h = httplib2.Http(".cache",
                          disable_ssl_certificate_validation=True)
        url = 'https://raw.github.com/heat-api/heat/master/templates/%s'
        url = url % template_name
        resp, template = h.request(url, "GET")
        if resp.status not in (200, 304):
            messages.error(self.request, 'URL returned status %s' % resp.status)
        return template

    def single(self, data_table, request, object_id):
        self.request = request
        template = self._get_template(object_id)
        # store the template so we can render it next
        cache.set('heat_template_' + request.user.username, template)
        cache.set('heat_template_name_' + request.user.username, object_id)
        return HttpResponseRedirect(reverse("horizon:thermal:stacks:launch"))


class ThermalCataloguesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Template Name"),
                           link=("horizon:thermal:stacks:detail"),)
    size = tables.Column("size", verbose_name=_("Size"))

    class Meta:
        name = "catalogue"
        verbose_name = _("Catalogues")
        #status_columns = ["status", ]
        #table_actions = (LaunchCatalogue, DeleteStack,)
        #row_class = CataloguesUpdateRow
        row_actions = (LaunchCatalogue, )
